# CREMA-D

Publishes `crema-d` on Artifactory.

## Prerequisites

[Java] must be installed.

## Publishing

Run `./gradlew publish`.

An [Artifactory] account with deploy permissions must be configured via
Gradle properties `artifactoryUser` and `artifactoryApiKey`.

[Artifactory]: https://artifactory.audeering.com/
[Java]: https://sdkman.io/sdks#java
