# Platform-Specific Deployment

<cite>
**Referenced Files in This Document**   
- [entitlements.mac.plist](file://frontend/build/entitlements.mac.plist)
- [notarize.js](file://frontend/build/notarize.js)
- [installer.nsh](file://frontend/build/installer.nsh)
- [electron-builder.yml](file://frontend/electron-builder.yml)
- [dev-app-update.yml](file://frontend/dev-app-update.yml)
- [build.sh](file://build.sh)
- [build.bat](file://build.bat)
- [opencontext.spec](file://opencontext.spec)
- [index.ts](file://frontend/src/main/index.ts)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [macOS Deployment Requirements](#macos-deployment-requirements)
3. [Windows Deployment Configuration](#windows-deployment-configuration)
4. [Linux Packaging and Integration](#linux-packaging-and-integration)
5. [Code Signing and Certificate Management](#code-signing-and-certificate-management)
6. [Common Deployment Issues](#common-deployment-issues)
7. [Conclusion](#conclusion)

## Introduction
MineContext is a cross-platform desktop application that requires specific deployment configurations for each operating system to meet platform security requirements, ensure proper installation behavior, and provide a seamless user experience. This document details the platform-specific deployment requirements for macOS, Windows, and Linux, including App Sandbox entitlements, notarization processes, installer behavior, packaging formats, and code signing procedures. The deployment system leverages Electron Builder for packaging and distribution, with custom configurations to address platform-specific needs.

## macOS Deployment Requirements

### App Sandbox Entitlements
MineContext's macOS build configuration includes specific entitlements defined in `entitlements.mac.plist` to enable critical functionality while maintaining security compliance. The entitlements file grants necessary permissions for the application to function properly under Apple's App Sandbox restrictions:

```xml
<key>com.apple.security.cs.allow-jit</key>
<true/>
<key>com.apple.security.cs.allow-unsigned-executable-memory</key>
<true/>
<key>com.apple.security.cs.allow-dyld-environment-variables</key>
<true/>
```

These entitlements are essential for the application's Python backend integration and dynamic code execution requirements. The `allow-jit` entitlement enables Just-In-Time compilation, which is necessary for certain Python operations. The `allow-unsigned-executable-memory` entitlement allows the application to allocate executable memory, required for the embedded Python interpreter. The `allow-dyld-environment-variables` entitlement permits the use of dynamic linker environment variables, facilitating proper library loading for the Python components.

The entitlements are inherited by the application through the `entitlementsInherit` field in the `electron-builder.yml` configuration, ensuring they are applied during the code signing process.

**Section sources**
- [entitlements.mac.plist](file://frontend/build/entitlements.mac.plist#L5-L10)
- [electron-builder.yml](file://frontend/electron-builder.yml#L43)

### Automated Notarization Process
To meet Apple's security requirements for distribution outside the Mac App Store, MineContext implements an automated notarization process using the `notarize.js` script. This script is triggered after the application is signed, as specified in the `afterSign` field of `electron-builder.yml`.

The notarization process requires three environment variables to be set:
- `APPLE_ID`: The Apple ID email address
- `APPLE_APP_SPECIFIC_PASSWORD`: An app-specific password for the Apple ID
- `APPLE_TEAM_ID`: The Apple Developer Team ID

The notarization script performs the following steps:
1. Checks if the build platform is macOS (darwin)
2. Validates that all required Apple credentials are available
3. Constructs the path to the signed application bundle
4. Submits the application to Apple's notarization service
5. Waits for the notarization process to complete

The script targets the bundle identifier `com.vikingdb.desktop` and uses the provided credentials to authenticate with Apple's notarization service. This automated process ensures that every macOS build is properly notarized, reducing the likelihood of Gatekeeper blocking the application on user systems.

**Section sources**
- [notarize.js](file://frontend/build/notarize.js#L3-L26)
- [electron-builder.yml](file://frontend/electron-builder.yml#L65)

## Windows Deployment Configuration

### Custom Installer Behavior
MineContext's Windows installer is configured with custom behavior through the `installer.nsh` script, which extends the default NSIS installer functionality provided by Electron Builder. The custom installer adds a dedicated page for selecting the application data directory, separate from the installation directory.

The installer implements the following key features:

**Data Directory Selection**: Users can choose where MineContext stores application data (databases, files, cache). The default location is `%LOCALAPPDATA%\MineContext`, but users can select a custom directory through a browse dialog.

**Validation Logic**: The installer validates the selected data directory with the following checks:
- Ensures the directory path is not empty
- Prevents the data directory from being the same as the installation directory
- Tests write permissions by creating and deleting a temporary file
- Creates the directory if it doesn't exist

**Registry Storage**: The selected data directory is stored in the Windows Registry under `HKCU\Software\MineContext\DataDirectory` for future reference.

**Installation Options**: The NSIS configuration in `electron-builder.yml` specifies:
- Desktop shortcut creation (always)
- User-level installation (perMachine: false)
- Custom installer and uninstaller icons
- Multi-page installer with ability to change installation directory

This custom installer behavior provides users with greater control over their data storage location while ensuring the application has the necessary permissions to function correctly.

**Section sources**
- [installer.nsh](file://frontend/build/installer.nsh#L1-L112)
- [electron-builder.yml](file://frontend/electron-builder.yml#L25-L37)

## Linux Packaging and Integration

### Packaging Format Considerations
MineContext supports multiple Linux packaging formats as configured in the `electron-builder.yml` file. The application is packaged as AppImage, Snap, and Debian packages to ensure broad compatibility across different Linux distributions.

**AppImage**: The primary distribution format for Linux, allowing users to run the application without installation. The AppImage format is configured with a custom artifact name pattern `${name}-${version}.${ext}` for consistent naming.

**Snap**: Provides sandboxed execution and automatic updates through the Snap store. Snap packages are signed and distributed through the Snapcraft store, offering an additional distribution channel.

**Debian Package**: Enables installation on Debian-based distributions (Ubuntu, Linux Mint, etc.) through the standard package manager, providing integration with the system's package management ecosystem.

The Linux build configuration also specifies:
- Maintainer information (electronjs.org)
- Application category (Utility)
- Custom artifact naming

### Desktop Integration
MineContext implements standard desktop integration for Linux systems:
- Desktop entry creation for application launcher integration
- Proper icon registration
- MIME type associations
- Menu categorization under "Utility"

The application's desktop entry includes the necessary metadata for proper display in application menus and launchers. The integration ensures that MineContext appears in the system's application menu with the correct icon and can be launched like any other native Linux application.

**Section sources**
- [electron-builder.yml](file://frontend/electron-builder.yml#L53-L62)

## Code Signing and Certificate Management

### Cross-Platform Code Signing
MineContext implements code signing for all platforms to ensure application integrity and reduce security warnings during installation.

**macOS Code Signing**: The application is signed using a Developer ID Application certificate. The `opencontext.spec` file contains logic to handle certificate management:
- Extracts the certificate from the `CSC_LINK` environment variable (base64-encoded PKCS#12)
- Creates a temporary keychain with a random password
- Imports the certificate into the temporary keychain
- Configures the keychain as the default for code signing
- Sets up proper keychain permissions for the codesign tool

This approach allows for secure certificate handling in CI/CD environments without exposing sensitive credentials.

**Windows Code Signing**: While not explicitly shown in the configuration files, Electron Builder typically uses the `CSC_LINK` and `CSC_KEY_PASSWORD` environment variables for Windows code signing with Authenticode certificates.

**Linux Code Signing**: AppImage and Snap packages are signed as part of their respective packaging processes, with Snap packages requiring signing through the Snapcraft infrastructure.

### Certificate Environment Variables
The code signing process relies on the following environment variables:
- `CSC_LINK`: Base64-encoded certificate file (PKCS#12 for macOS, PFX for Windows)
- `CSC_KEY_PASSWORD`: Password for the certificate file
- `APPLE_ID`, `APPLE_APP_SPECIFIC_PASSWORD`, `APPLE_TEAM_ID`: Apple credentials for notarization

The certificate management in `opencontext.spec` ensures that the temporary keychain is properly cleaned up after the build process, maintaining security best practices.

**Section sources**
- [opencontext.spec](file://opencontext.spec#L11-L73)
- [electron-builder.yml](file://frontend/electron-builder.yml#L65)

## Common Deployment Issues

### Antivirus False Positives
Electron applications that bundle Python interpreters and execute dynamic code are often flagged by antivirus software as potentially malicious. This occurs because:
- The application generates executable code at runtime
- It uses dynamic library loading
- It may exhibit behavior similar to packers or obfuscators

**Mitigation Strategies**:
- Submit the application to antivirus vendors for whitelisting
- Use consistent code signing certificates
- Implement the minimum necessary entitlements
- Provide clear documentation about the application's behavior

### Permission Errors
Permission issues commonly occur during installation and runtime:

**macOS**: App Sandbox restrictions may prevent access to certain directories. The entitlements configuration addresses this by requesting necessary permissions.

**Windows**: The custom installer validates write permissions before proceeding with installation, preventing runtime errors due to insufficient privileges.

**Linux**: AppImage execution may be blocked by default on some distributions. Users may need to mark the file as executable or use specific launch methods.

### Auto-Update Configuration
MineContext uses electron-updater for automatic updates, configured through the `dev-app-update.yml` file:

```yaml
provider: github
owner: volcengine
repo: MineContext
updaterCacheDirName: minecontext-updater
```

**Common Update Issues**:
- Network connectivity problems preventing update checks
- Permission errors when replacing application files
- Antivirus software blocking update downloads
- Certificate validation failures

The update process is integrated into the main application through the `autoUpdater` module in Electron, with logging configured to the main application logger for troubleshooting.

**Section sources**
- [dev-app-update.yml](file://frontend/dev-app-update.yml#L1-L5)
- [index.ts](file://frontend/src/main/index.ts#L29)

## Conclusion
MineContext's deployment strategy addresses the unique requirements of each platform while maintaining a consistent user experience. The configuration balances security compliance with functional requirements, particularly in the handling of entitlements on macOS and custom installer behavior on Windows. The automated notarization process and comprehensive code signing approach ensure that the application meets platform security standards. For Linux, multiple packaging formats provide flexibility for different user preferences and distribution channels. The deployment system is designed to be robust and maintainable, with clear separation of platform-specific configurations and automated processes to reduce human error in the release workflow.