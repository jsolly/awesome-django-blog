#!/usr/bin/env bash
# Shared Cursor Cloud install helpers. Source from repo scripts/cloud-agent-install.sh:
#   source "$(cd "$(dirname "$0")/.." && pwd)/.agents/scripts/cloud-install-lib.sh"
#
# Provides: install_zip_unzip, install_sam, install_yaml_linters

install_zip_unzip() {
	if ! command -v apt-get >/dev/null 2>&1; then
		return 0
	fi
	for pkg in zip unzip; do
		if ! command -v "$pkg" >/dev/null 2>&1; then
			sudo apt-get update -qq
			sudo apt-get install -y -qq zip unzip
			break
		fi
	done
}

install_sam() {
	install_zip_unzip
	if command -v sam >/dev/null 2>&1; then
		sam --version
		return 0
	fi
	local arch sam_arch
	arch="$(uname -m)"
	case "$arch" in
		aarch64 | arm64) sam_arch=arm64 ;;
		x86_64 | amd64) sam_arch=x86_64 ;;
		*)
			echo "Unsupported architecture for SAM CLI install: $arch" >&2
			exit 1
			;;
	esac
	curl -fsSL "https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-${sam_arch}.zip" \
		-o /tmp/sam.zip
	unzip -q /tmp/sam.zip -d /tmp/sam
	sudo /tmp/sam/install
	sam --version
}

install_yaml_linters() {
	# Pin versions to match stocktextalerts CI (noDeploy.yml).
	if ! command -v yamllint >/dev/null 2>&1; then
		if command -v pipx >/dev/null 2>&1; then
			pipx install yamllint==1.38.0
		elif command -v pip3 >/dev/null 2>&1; then
			pip3 install --user yamllint==1.38.0
		else
			echo "yamllint not found and pipx/pip3 unavailable" >&2
			exit 1
		fi
	fi
	if ! command -v actionlint >/dev/null 2>&1; then
		bash <(curl -sSf https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash) 1.7.12
		sudo mv actionlint /usr/local/bin/actionlint
	fi
	yamllint --version
	actionlint -version
}
