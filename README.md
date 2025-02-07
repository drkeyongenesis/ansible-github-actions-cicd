### **Tutorial: Automating CI/CD with GitHub Actions for Docker and Ansible Playbooks**

#### **Tutorial Overview**
In this tutorial, we will automate the process of:
1. **Running Ansible Playbooks**: Testing and validating Ansible playbooks during the CI process.
2. **Docker Image Build and Push**: Building and pushing Docker images to GitHub Container Registry (GHCR).
3. **Release and Tag Management**: Creating Git tags and releases for versioning.

This updated version will focus on testing Ansible playbooks within the CI/CD pipeline, in addition to building Docker images and managing releases.

This workflow integrates testing of Ansible playbooks into the CI pipeline using GitHub Actions. If the playbooks pass, the Docker image will be built and tagged. If the playbooks fail, the pipeline will stop, preventing any Docker builds or releases.

---

### **Step 1: Setting Up the Workflow File**

We’ll define our workflow in `.github/workflows/ci-main.yml`. The steps include checking the commit message for the `--no-ci` flag, validating Git tags, testing Ansible playbooks, building Docker images, and managing releases.

---

### **Step 2: Initialize the Workflow**

This step will initialize the workflow, check for specific flags in the commit message, and verify the existence of version tags.

```yaml
name: ci-main

on:
  push:
    branches:
      - main

jobs:
  init:
    name: 🧐 Initialize
    runs-on: ubuntu-24.04-arm
    outputs:
      skip_ci: ${{ steps.check_flag.outputs.skip_ci }}
      image_version: ${{ steps.check_tag.outputs.image_version }}
      tag_exists: ${{ steps.check_tag.outputs.tag_exists }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Check for --no-ci flag in commit message
        id: check_flag
        run: |
          echo "Checking commit message for --no-ci flag..."
          if echo "${{ github.event.head_commit.message }}" | grep -- '--no-ci'; then
            echo "Skipping CI"
            echo "skip_ci=true" >> $GITHUB_OUTPUT
          else
            echo "skip_ci=false" >> $GITHUB_OUTPUT
          fi

      - name: Check release tag
        id: check_tag
        run: |
          VERSION=$(cat requirements.txt | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+')
          echo "image_version=v${VERSION}" >> $GITHUB_OUTPUT
      
          export TAG_NAME="v${VERSION}"
          if ! [[ "$TAG_NAME" =~ ^v[0-9]+\.[0-9]+(\.[0-9]+)?$ ]]; then
            echo "Tag $TAG_NAME does not meet the required format 'vX.Y.Z'."
            exit 1
          fi

          git fetch --unshallow --tags
          export TAG_EXISTS=$(git tag --list $TAG_NAME)
          if [ -n "$TAG_EXISTS" ]; then
            echo "Tag $TAG_NAME already exists."
            echo "tag_exists=true" >> $GITHUB_OUTPUT
          else
            echo "tag_exists=false" >> $GITHUB_OUTPUT
          fi
```

**Explanation:**
- **Check for `--no-ci` Flag**: Prevents the CI pipeline from running if the commit message contains `--no-ci`.
- **Check for Version Tags**: Ensures that the version extracted from the `requirements.txt` file exists as a tag in the repository.

---

### **Step 3: Test Ansible Playbooks**

We’ll add a step to test your Ansible playbooks before any Docker images are built. This will help ensure the playbooks are working as expected.

```yaml
  test_ansible:
    name: 🧪 Test Ansible Playbooks
    needs: init
    runs-on: ubuntu-24.04-arm
    if: ${{ needs.init.outputs.skip_ci == 'false' }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Ansible
        run: |
          sudo apt update
          sudo apt install -y ansible

      - name: Test Ansible Playbooks
        run: |
          echo "Running Ansible playbooks tests..."
          ansible-playbook -i inventory/localhost, playbooks/test-playbook.yml --check --diff
```

**Explanation:**
- **Set Up Ansible**: Installs Ansible on the runner.
- **Run Ansible Playbooks**: The playbook is tested using the `--check` and `--diff` options. The `--check` option performs a dry-run without making any changes, and `--diff` shows what changes would be made.

If the playbook fails, the job will stop, preventing the Docker build from running.

---

### **Step 4: Build Docker Image and Push to GitHub Container Registry**

If the Ansible playbooks pass successfully, we’ll proceed with building and pushing the Docker image.

```yaml
  build:
    name: 🏗️ Build Docker Image
    needs: test_ansible
    if: ${{ needs.test_ansible.result == 'success' && needs.init.outputs.skip_ci == 'false' && needs.init.outputs.tag_exists == 'false' }}
    runs-on: ubuntu-24.04-arm
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and Push Docker Image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile
          platforms: linux/amd64,linux/arm64
          push: true
          provenance: false
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ needs.init.outputs.image_version }}
```

**Explanation:**
- **Docker Build and Push**: If the Ansible playbooks are successful and the tag doesn’t already exist, the Docker image is built and pushed to GitHub Container Registry (GHCR).

---

### **Step 5: Release and Tag Management**

If the Docker image is successfully built, we’ll create a Git tag and release.

```yaml
  release:
    name: 🚀 Release
    needs: [ init, build ]
    runs-on: ubuntu-24.04-arm
    steps:
      - name: Set version and push tag
        id: tag_version
        uses: mathieudutour/github-tag-action@v6.2
        with:
          tag_prefix: ""
          custom_tag: ${{ needs.init.outputs.image_version }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
          release_branches: main
          create_annotated_tag: false
          fetch_all_tags: false
          dry_run: false

      - name: Create Release
        uses: ncipollo/release-action@v1
        with:
          tag: ${{ needs.init.outputs.image_version }}
          name: "Ansible ${{ needs.init.outputs.image_version }}"
          token: ${{ secrets.GITHUB_TOKEN }}
          body: ${{ steps.tag_version.outputs.changelog }}
```

**Explanation:**
- **Git Tag**: A version tag is created based on the image version and pushed to GitHub.
- **Release**: A release is created with the specified tag and changelog.

---

### **Step 6: Final Workflow Overview**

Here’s a summary of the steps and logic in the workflow:

1. **Initialization**: Checks if CI should be skipped and verifies tag existence.
2. **Test Ansible Playbooks**: Runs Ansible playbooks to ensure they work correctly. If the playbooks fail, the pipeline stops.
3. **Build Docker Image**: If the playbooks pass, the Docker image is built and pushed to GHCR.
4. **Release and Tag**: Tags the release and creates a GitHub release based on the version.

---

### **Conclusion**

By following this tutorial, you’ve automated the testing of Ansible playbooks and integrated it with a full CI/CD pipeline for Docker images and releases. This workflow ensures that only tested and validated code gets built and released, which improves the quality and reliability of your deployments.

---

### **Optional Hands-on Exercises**:
1. **Modify the Playbook**: Add another playbook to your project and modify the CI pipeline to test both playbooks.
2. **Add Additional Ansible Tests**: Explore using `ansible-lint` or `yamllint` to perform additional checks on the playbooks before running them.

Would you like further details on any part of this workflow or have any specific questions?
