# Changelog

## [0.3.0](https://github.com/ACROSS-Team/across-server/compare/v0.2.1...v0.3.0) (2025-07-24)


### Features

* add Hubble observatory data migration ([#283](https://github.com/ACROSS-Team/across-server/issues/283)) ([6a22bf6](https://github.com/ACROSS-Team/across-server/commit/6a22bf625705bd053067ac0e0873ab76b19e4fd9))
* **api:** add interface for instrument Filter ([#285](https://github.com/ACROSS-Team/across-server/issues/285)) ([ea1f815](https://github.com/ACROSS-Team/across-server/commit/ea1f815b1da9f9f6de36eb08c8e744045e612621))

## [0.2.1](https://github.com/ACROSS-Team/across-server/compare/v0.2.0...v0.2.1) (2025-07-21)


### Bug Fixes

* add missing backslash command for migrate ([#307](https://github.com/ACROSS-Team/across-server/issues/307)) ([b6e9edc](https://github.com/ACROSS-Team/across-server/commit/b6e9edc02425dc2cfdf44902b1c4ab7399bd3f9c))
* add return type ([#309](https://github.com/ACROSS-Team/across-server/issues/309)) ([be251be](https://github.com/ACROSS-Team/across-server/commit/be251be2682254e7130dd59201d19c4104cb618e))
* **docs:** display build version on subapps ([#305](https://github.com/ACROSS-Team/across-server/issues/305)) ([b270a68](https://github.com/ACROSS-Team/across-server/commit/b270a68ff5b58127dab8c4f1bfc3ea4b1a7c4b38))

## [0.2.0](https://github.com/ACROSS-Team/across-server/compare/v0.1.1...v0.2.0) (2025-07-18)


### Features

* **lint:** add commitlint on PR titles ([#299](https://github.com/ACROSS-Team/across-server/issues/299)) ([9768191](https://github.com/ACROSS-Team/across-server/commit/976819146d2aba9fc74d45eaeb86db5538aef76f))


### Bug Fixes

* **deploy:** increase timeout to 30m ([ffa8311](https://github.com/ACROSS-Team/across-server/commit/ffa83118d70578d1c52f624335c0550574c0b81a))
* do not cancel in progress for lint, it doesn't restart ([50c3e2b](https://github.com/ACROSS-Team/across-server/commit/50c3e2b27e7d08c864744ab3dbbf0d64262a36ce))
* **gha:** proper glob matching for feature workflow trigger ([08dfe78](https://github.com/ACROSS-Team/across-server/commit/08dfe78bd3cd4b085d1ae434f882d375841e508d))
* increase deploymnet timeout ([fc37748](https://github.com/ACROSS-Team/across-server/commit/fc3774855e1f609784a15d96a352132bed8f3a73))

## [0.1.1](https://github.com/ACROSS-Team/across-server/compare/v0.1.0...v0.1.1) (2025-07-18)


### Bug Fixes

* **release:** run release-pr on push to main ([#300](https://github.com/ACROSS-Team/across-server/issues/300)) ([e8c5295](https://github.com/ACROSS-Team/across-server/commit/e8c529553c51c1efebaaceea3452d7d8574f4a56))

## 0.1.0 (2025-07-17)


### ⚠ BREAKING CHANGES

* delete create role route ([#288](https://github.com/ACROSS-Team/across-server/issues/288))
* create role route is deleted

### Features

* add `release-please` and `release` gh workflows to deploy staging and prod ([#290](https://github.com/ACROSS-Team/across-server/issues/290)) ([0791415](https://github.com/ACROSS-Team/across-server/commit/07914152541ba8b2f2a93c3513699be658f43b10))
* add Chandra data migration ([#262](https://github.com/ACROSS-Team/across-server/issues/262)) ([aeadbdb](https://github.com/ACROSS-Team/across-server/commit/aeadbdb00a333c5ae5daa036e484b24d28816aa7))
* add development commands and an ask 'fn' ([afcea4b](https://github.com/ACROSS-Team/across-server/commit/afcea4ba2ac7b88c401e5a40ea1e297454241de1))
* add email functionality to user creation and login ([#64](https://github.com/ACROSS-Team/across-server/issues/64)) ([898dcf8](https://github.com/ACROSS-Team/across-server/commit/898dcf82147c06460eb05617d6ea4b6ce9693297))
* add help command to Makefile ([afcea4b](https://github.com/ACROSS-Team/across-server/commit/afcea4ba2ac7b88c401e5a40ea1e297454241de1))
* Add nicer data migration ([#259](https://github.com/ACROSS-Team/across-server/issues/259)) ([e812532](https://github.com/ACROSS-Team/across-server/commit/e812532825041ba56c7b3f687f13a63ca79a6901))
* add nustar observatory migration ([#245](https://github.com/ACROSS-Team/across-server/issues/245)) ([66db486](https://github.com/ACROSS-Team/across-server/commit/66db48613368e02f397b91adb69572bc2b3ccfb6))
* add observatory/telescope/instrument metadata parameters ([#199](https://github.com/ACROSS-Team/across-server/issues/199)) ([d570c6d](https://github.com/ACROSS-Team/across-server/commit/d570c6d1bace454c56aacb99a4be7a6aaa6e2c64))
* add post observation endpoint ([#16](https://github.com/ACROSS-Team/across-server/issues/16)) ([b1cdf9c](https://github.com/ACROSS-Team/across-server/commit/b1cdf9c1badfb4142de85e0ca2295e9bd2f0b129))
* add Swift observatory data ([#265](https://github.com/ACROSS-Team/across-server/issues/265)) ([c98efdc](https://github.com/ACROSS-Team/across-server/commit/c98efdccb8f8c99c70a214ab49adc8094f95860f))
* **api:** use subapps for versioning ([a75412e](https://github.com/ACROSS-Team/across-server/commit/a75412ec87f959b9e3a033139743d3e6c3bb4558))
* **auth:** add client_credentials auth flow for service account access ([#246](https://github.com/ACROSS-Team/across-server/issues/246)) ([56055d9](https://github.com/ACROSS-Team/across-server/commit/56055d981225c67cefc6bdf51db1bbbf23fd17e6))
* **build:** Alter `make lock` so it rebuilds lock files for all environments ([#84](https://github.com/ACROSS-Team/across-server/issues/84)) ([f9b4830](https://github.com/ACROSS-Team/across-server/commit/f9b4830200c1f07a356bbccb271405c0fbbe942c))
* change pixi for Makefile and uv for dep management. Adjust Dockerfile as needed for usage. ([afcea4b](https://github.com/ACROSS-Team/across-server/commit/afcea4ba2ac7b88c401e5a40ea1e297454241de1))
* change pixi for Makefile and uv for dep mgmt. Adjust Dockerfile as needed for usage. ([afcea4b](https://github.com/ACROSS-Team/across-server/commit/afcea4ba2ac7b88c401e5a40ea1e297454241de1))
* **cicd:** add deployment GHA workflows for feature branch ([#244](https://github.com/ACROSS-Team/across-server/issues/244)) ([670976b](https://github.com/ACROSS-Team/across-server/commit/670976b3e78b36eb2f7a1a1be806dd41fa8cc243))
* convert `pixi` to `uv` with the usage of a Makefile for project commands ([#10](https://github.com/ACROSS-Team/across-server/issues/10)) ([afcea4b](https://github.com/ACROSS-Team/across-server/commit/afcea4ba2ac7b88c401e5a40ea1e297454241de1))
* **db:** add ability to connect to AWS aurora cluster ([#207](https://github.com/ACROSS-Team/across-server/issues/207)) ([d2c2c52](https://github.com/ACROSS-Team/across-server/commit/d2c2c52e19c59499d5c0736628ce2af90b2dce59))
* **db:** convert necessary seeds into migrations for deployment ([#227](https://github.com/ACROSS-Team/across-server/issues/227)) ([f85af64](https://github.com/ACROSS-Team/across-server/commit/f85af642ae34327ab6febb8896c0c33e0c7df749))
* **docker:** buildable server image tagged by SHA by default, add TYPE_CHECKING check ([#224](https://github.com/ACROSS-Team/across-server/issues/224)) ([3812982](https://github.com/ACROSS-Team/across-server/commit/381298259a39ab85c4e19a50e1c3dd039f28c75c))
* GET endpoints for Observatory, Telescope, and Instrument ([#138](https://github.com/ACROSS-Team/across-server/issues/138)) ([e09ae77](https://github.com/ACROSS-Team/across-server/commit/e09ae77db93ad00639d33823bc9e1474bb69d0c2))
* **group_role:** add group role crud and assign/remove role to user management system ([#186](https://github.com/ACROSS-Team/across-server/issues/186)) ([dd4dd73](https://github.com/ACROSS-Team/across-server/commit/dd4dd737f394704f4f9207a8ac51bdf833a845c9))
* init design and structure of server ([#1](https://github.com/ACROSS-Team/across-server/issues/1)) ([de9c4bd](https://github.com/ACROSS-Team/across-server/commit/de9c4bd5b461c0a77e3b7a3a445228b76af9850a))
* **invite:** add user invitation and removal to user group management system ([#208](https://github.com/ACROSS-Team/across-server/issues/208)) ([2ae0ebc](https://github.com/ACROSS-Team/across-server/commit/2ae0ebce2b11799f3a81156cc99407602a15262b))
* **limiter:** add rate limiting with conditional limits ([#261](https://github.com/ACROSS-Team/across-server/issues/261)) ([c84baa1](https://github.com/ACROSS-Team/across-server/commit/c84baa19640679034a711050deadef105f89d4f4))
* **logging:** add `structlog`, correlation IDs, and custom logging middleware ([#137](https://github.com/ACROSS-Team/across-server/issues/137)) ([3877bdc](https://github.com/ACROSS-Team/across-server/commit/3877bdca06ad947521c1ae5dfdcb14456fe439fd))
* main deploy to dev ([#276](https://github.com/ACROSS-Team/across-server/issues/276)) ([ab67a11](https://github.com/ACROSS-Team/across-server/commit/ab67a11071dcaf4c20b115a6d9d0ea384224b5d6))
* **migration:** observatory migration for ixpe ([#212](https://github.com/ACROSS-Team/across-server/issues/212)) ([1f679f0](https://github.com/ACROSS-Team/across-server/commit/1f679f0404a0cd10e1a8def3827ed638f78beec7))
* **migrations:** add functions to build ssa records and delete, to avoid duplicative code ([4bd3dcc](https://github.com/ACROSS-Team/across-server/commit/4bd3dcc6ad24e51597407dd118a25612a9ce0c1c))
* mv docker files to containers dir, fix missing check for uv ([afcea4b](https://github.com/ACROSS-Team/across-server/commit/afcea4ba2ac7b88c401e5a40ea1e297454241de1))
* **observation:** GET and GET Many ([#228](https://github.com/ACROSS-Team/across-server/issues/228)) ([e4177fa](https://github.com/ACROSS-Team/across-server/commit/e4177fa390f3154b5e092bb29b7fc43c63828600))
* **observatory:** Add ephemeris type and ephemeris parameters to `/observatory` endpoint ([#190](https://github.com/ACROSS-Team/across-server/issues/190)) ([1ca62fa](https://github.com/ACROSS-Team/across-server/commit/1ca62faf875a78ab30cc47f118581fb4b3c7ba32))
* **pagination:** add pagination filtering parameters to schedule routes ([#253](https://github.com/ACROSS-Team/across-server/issues/253)) ([1897b52](https://github.com/ACROSS-Team/across-server/commit/1897b52966cf489823a05fe1e125cd4d42702d94))
* **role:** create user service_account group_role router and service ([#134](https://github.com/ACROSS-Team/across-server/issues/134)) ([fab2b49](https://github.com/ACROSS-Team/across-server/commit/fab2b49c1e00bff25799f9b380c3f8da39b7c3a2))
* schedule API ([#105](https://github.com/ACROSS-Team/across-server/issues/105)) ([c3030ae](https://github.com/ACROSS-Team/across-server/commit/c3030ae755c4f8eb677e534a4f45a2194fa8aafb))
* Schedule API (get, post) ([c3030ae](https://github.com/ACROSS-Team/across-server/commit/c3030ae755c4f8eb677e534a4f45a2194fa8aafb))
* **schedule:** add bulk schedule create ([#258](https://github.com/ACROSS-Team/across-server/issues/258)) ([4198894](https://github.com/ACROSS-Team/across-server/commit/41988947c920485f39cdf23a249834495a8f58e2))
* **server:** Add FOV type for instruments, and validate schedules and observations for instruments ([#220](https://github.com/ACROSS-Team/across-server/issues/220)) ([273b34f](https://github.com/ACROSS-Team/across-server/commit/273b34f4d834c7da37b9e12449368179479ae189))
* **server:** Add service account models and API ([#59](https://github.com/ACROSS-Team/across-server/issues/59)) ([3aa25fb](https://github.com/ACROSS-Team/across-server/commit/3aa25fb42a6406d9b73facb2095c50c1ccf5f0b3))
* **slew:** support slew surveys for observation type enum ([#268](https://github.com/ACROSS-Team/across-server/issues/268)) ([7243f8e](https://github.com/ACROSS-Team/across-server/commit/7243f8e18735e9815159409df67d945f3d9f62d5))
* **tle:** Create TLE Service with POST endpoint ([#88](https://github.com/ACROSS-Team/across-server/issues/88)) ([d2d97ee](https://github.com/ACROSS-Team/across-server/commit/d2d97eed473a20af1b051da3fa9922c8ef5327d5))


### Bug Fixes

* Allow User to do from_attributes ([42af211](https://github.com/ACROSS-Team/across-server/commit/42af211ddd0378e6a6890d6b704f15cfe670f16c))
* **api:** Remove /observation endpoint as it's not used and incorrectly defined ([#193](https://github.com/ACROSS-Team/across-server/issues/193)) ([be9c8eb](https://github.com/ACROSS-Team/across-server/commit/be9c8ebdbcd5d89f42cd810388d50352464ee5e5))
* **api:** Remove /observation endpoint as it's not used and incorrectly defined. ([be9c8eb](https://github.com/ACROSS-Team/across-server/commit/be9c8ebdbcd5d89f42cd810388d50352464ee5e5))
* **auth:** Fix crash in /auth/login, send HTTP exception instead ([4ac0e4f](https://github.com/ACROSS-Team/across-server/commit/4ac0e4ffcccbb8817629f13c5c1998384863e3ec))
* **auth:** Fix crash in `/auth/login`, send HTTP exception instead ([#275](https://github.com/ACROSS-Team/across-server/issues/275)) ([4ac0e4f](https://github.com/ACROSS-Team/across-server/commit/4ac0e4ffcccbb8817629f13c5c1998384863e3ec))
* **build:** Fix `mypy` path in Makefile ([#49](https://github.com/ACROSS-Team/across-server/issues/49)) ([169a764](https://github.com/ACROSS-Team/across-server/commit/169a764bc9c7e2d0559ff38f3beee256a8a90c60))
* **build:** Remove option that was causing `make build` to fail ([#240](https://github.com/ACROSS-Team/across-server/issues/240)) ([0527e8f](https://github.com/ACROSS-Team/across-server/commit/0527e8f2881ad1ff804412e2214af716c096cc37))
* **build:** Remove option that was making make build fail ([0527e8f](https://github.com/ACROSS-Team/across-server/commit/0527e8f2881ad1ff804412e2214af716c096cc37))
* **build:** Unpin dependencies to allow dependabot to fix security issues ([#87](https://github.com/ACROSS-Team/across-server/issues/87)) ([5929445](https://github.com/ACROSS-Team/across-server/commit/59294451d9d94c247328f34e3ca0c60c62bd8309))
* **build:** Unpin dependencies, particularly fastapi to allow dependabot to fix a high security alert on starlette ([5929445](https://github.com/ACROSS-Team/across-server/commit/59294451d9d94c247328f34e3ca0c60c62bd8309))
* Correct return types for `/user/{user_id}/service-account/{service_account_id}/group-role` endpoint ([#173](https://github.com/ACROSS-Team/across-server/issues/173)) ([2cec458](https://github.com/ACROSS-Team/across-server/commit/2cec458e95084796502c24226164ae7ddf6770e8))
* **db:** add pre ping parameter to db async engine to resolve database connection reset errors ([#203](https://github.com/ACROSS-Team/across-server/issues/203)) ([9a46f6b](https://github.com/ACROSS-Team/across-server/commit/9a46f6bab6e235fd18ce0fc4edf67e8e8997ce30))
* **db:** migrations missing schema, revision heads adjusted, init filename will be first ([#214](https://github.com/ACROSS-Team/across-server/issues/214)) ([857ab86](https://github.com/ACROSS-Team/across-server/commit/857ab863b3148a7e1d44af4899dd96e1de08c2dd))
* **db:** new migrations new check appropriate schemas ([#217](https://github.com/ACROSS-Team/across-server/issues/217)) ([d972886](https://github.com/ACROSS-Team/across-server/commit/d9728866867ea5e1e143526c206aa2ebd746f7e8))
* **db:** UTC time not enforced in database `created_on` and `modified_on` ([#126](https://github.com/ACROSS-Team/across-server/issues/126)) ([fc09979](https://github.com/ACROSS-Team/across-server/commit/fc0997933b34f272c945bb81070285338f63703d))
* **env:** update env var names and values to fix sending emails ([#218](https://github.com/ACROSS-Team/across-server/issues/218)) ([1267af1](https://github.com/ACROSS-Team/across-server/commit/1267af1f876c373b7a35954e8d1b92375d0c8ed0))
* **exception:** Clarify exception for TLE not found ([d2d97ee](https://github.com/ACROSS-Team/across-server/commit/d2d97eed473a20af1b051da3fa9922c8ef5327d5))
* **group-role:** add  to prefix, remove unused code ([c13bed6](https://github.com/ACROSS-Team/across-server/commit/c13bed6f9be679afd755a22ae11ac2b7ed22c9ed))
* **group-role:** add `group` to prefix, remove unused code ([#101](https://github.com/ACROSS-Team/across-server/issues/101)) ([c13bed6](https://github.com/ACROSS-Team/across-server/commit/c13bed6f9be679afd755a22ae11ac2b7ed22c9ed))
* **group:** add read groups permission ([#102](https://github.com/ACROSS-Team/across-server/issues/102)) ([d97e2fa](https://github.com/ACROSS-Team/across-server/commit/d97e2faddf708de100a05f9caf9eea4de34b93cf))
* **hard_reset:** add ssh default and platform linux/amd64 to docker-compose.local ([#230](https://github.com/ACROSS-Team/across-server/issues/230)) ([9974e1c](https://github.com/ACROSS-Team/across-server/commit/9974e1ce475faacfd5bacf33a757187ee29e63ea))
* **hard_reset:** add ssh default and platform linux/amd64 to docker-compose.local and remove docker-compose.prod because it is not used ([9974e1c](https://github.com/ACROSS-Team/across-server/commit/9974e1ce475faacfd5bacf33a757187ee29e63ea))
* **instrument:** Fix instrument search based on telescope ID or name ([#252](https://github.com/ACROSS-Team/across-server/issues/252)) ([f4837c5](https://github.com/ACROSS-Team/across-server/commit/f4837c54cdd51e6fe826ba9054b1161e9688dc93))
* **lint:** Change `make lint` to lint all files. ([#159](https://github.com/ACROSS-Team/across-server/issues/159)) ([030f877](https://github.com/ACROSS-Team/across-server/commit/030f8779d8a8395ed0009ce1a7d4243b948a3c76))
* **migration:** Added missing primary_key definitions to TLE migration ([d2d97ee](https://github.com/ACROSS-Team/across-server/commit/d2d97eed473a20af1b051da3fa9922c8ef5327d5))
* **migration:** Edit the create TESS migration so that it adds group admin role ([#233](https://github.com/ACROSS-Team/across-server/issues/233)) ([3499d2e](https://github.com/ACROSS-Team/across-server/commit/3499d2e3c53cb81847ee1df8167eac657670f257))
* **migrations:** Hotfix for make reset ([#162](https://github.com/ACROSS-Team/across-server/issues/162)) ([84ef2ab](https://github.com/ACROSS-Team/across-server/commit/84ef2abdb0e235372d050d2c0c5f6c66ded44e3b))
* **python:** Update code to be uniformly Python 3.12 compliant ([#129](https://github.com/ACROSS-Team/across-server/issues/129)) ([f692e02](https://github.com/ACROSS-Team/across-server/commit/f692e02a96b3367481ad83f5e7e0b99a39ab9cb9))
* **release:** add missing token inputs ([0abce02](https://github.com/ACROSS-Team/across-server/commit/0abce02c1fcf281c458f297514d63352d62a6b03))
* Remove inadvertant code commit ([42af211](https://github.com/ACROSS-Team/across-server/commit/42af211ddd0378e6a6890d6b704f15cfe670f16c))
* remove logging middleware in mounted app to prevent dupe logs ([#267](https://github.com/ACROSS-Team/across-server/issues/267)) ([094fb40](https://github.com/ACROSS-Team/across-server/commit/094fb403926aebef20e15e7fd2d50b47401b3469))
* **test:** Add test for schemas.TLE conversion of epoch to datetime. Fixes. ([d2d97ee](https://github.com/ACROSS-Team/across-server/commit/d2d97eed473a20af1b051da3fa9922c8ef5327d5))
* **tests:** fix hanging email service test ([#136](https://github.com/ACROSS-Team/across-server/issues/136)) ([6cbd979](https://github.com/ACROSS-Team/across-server/commit/6cbd979d930e46399eae19f5a71b058071bcb1b3))
* **tests:** Move `mock_global_access` and `mock_self_access` to top level `conftest.py` ([#98](https://github.com/ACROSS-Team/across-server/issues/98)) ([c6c1283](https://github.com/ACROSS-Team/across-server/commit/c6c1283010cace7a430c614710bb2b7260f1976b))
* **tests:** Move mock_global_access and mock_self_access to top level conftest.py ([c6c1283](https://github.com/ACROSS-Team/across-server/commit/c6c1283010cace7a430c614710bb2b7260f1976b))
* **tests:** Move things into conftest.py ([d2d97ee](https://github.com/ACROSS-Team/across-server/commit/d2d97eed473a20af1b051da3fa9922c8ef5327d5))
* **tle:** Fix exists logic ([d2d97ee](https://github.com/ACROSS-Team/across-server/commit/d2d97eed473a20af1b051da3fa9922c8ef5327d5))
* **tle:** Remove id from TLE model, as it means norad_id + epoch no longer are a unique entry ([d2d97ee](https://github.com/ACROSS-Team/across-server/commit/d2d97eed473a20af1b051da3fa9922c8ef5327d5))
* **tle:** When TLE is not found return None (as per tech spec) ([d2d97ee](https://github.com/ACROSS-Team/across-server/commit/d2d97eed473a20af1b051da3fa9922c8ef5327d5))
* **type:** Require typed functions/methods in mypy. Add pydantic plugin. ([#148](https://github.com/ACROSS-Team/across-server/issues/148)) ([ea33124](https://github.com/ACROSS-Team/across-server/commit/ea331249a01e0ec8ab616c0657f496de22f595a4))
* **types:** Add missing type decoration to entire repo ([#167](https://github.com/ACROSS-Team/across-server/issues/167)) ([ada6987](https://github.com/ACROSS-Team/across-server/commit/ada69872d59ec25ab1d48acf474d7987d94a36c3))
* **types:** Correct returns to be Pydantic instead of SQLA ([4af3cae](https://github.com/ACROSS-Team/across-server/commit/4af3caeff4747303a7d7bf12cfecbd9d26f0e259))
* **types:** Fix /role endpoints to return Pydantic Schema, not SQLA Models ([#163](https://github.com/ACROSS-Team/across-server/issues/163)) ([42af211](https://github.com/ACROSS-Team/across-server/commit/42af211ddd0378e6a6890d6b704f15cfe670f16c))
* **types:** Fix return types for /group endpoints to Pydantic schema ([#169](https://github.com/ACROSS-Team/across-server/issues/169)) ([26b6eff](https://github.com/ACROSS-Team/across-server/commit/26b6eff5d02a5c119ff99eb365f29444e7191043))
* **types:** For `/user/{user_id}/service_account` endpoints, correct returns to be Pydantic instead of SQLA ([#165](https://github.com/ACROSS-Team/across-server/issues/165)) ([4af3cae](https://github.com/ACROSS-Team/across-server/commit/4af3caeff4747303a7d7bf12cfecbd9d26f0e259))
* **types:** Return pydantic schema for /user endpoints ([#164](https://github.com/ACROSS-Team/across-server/issues/164)) ([9dd15e9](https://github.com/ACROSS-Team/across-server/commit/9dd15e9c03f3ee0f2f409a8d3a9373642b2c0850))
* **typing:** Fix typing of `Telescope` model `observatory_id` attribute ([#156](https://github.com/ACROSS-Team/across-server/issues/156)) ([4092714](https://github.com/ACROSS-Team/across-server/commit/4092714294ba6c581c0ab996cd857f0c44f86778))
* **typing:** Remove last `Optional`s. Fix use of Optional where default is not `None`. ([#145](https://github.com/ACROSS-Team/across-server/issues/145)) ([f0c43b1](https://github.com/ACROSS-Team/across-server/commit/f0c43b1b84cb0cfcc313a36b5dc671c07f524d88))
* Update all `from_orm` constructors to be class methods ([#238](https://github.com/ACROSS-Team/across-server/issues/238)) ([919b17e](https://github.com/ACROSS-Team/across-server/commit/919b17e8c4c409fdfe3fccc2cb0c24e8d26cb411))
* updating a user without all fields present ([#38](https://github.com/ACROSS-Team/across-server/issues/38)) ([ef82f96](https://github.com/ACROSS-Team/across-server/commit/ef82f96c0fe4d91429d939dc801d39142d9b1360))
* Use BaseSchema instead of BaseModel ([42af211](https://github.com/ACROSS-Team/across-server/commit/42af211ddd0378e6a6890d6b704f15cfe670f16c))
* **user:** add character restrictions to string inputs ([#112](https://github.com/ACROSS-Team/across-server/issues/112)) ([0b0182f](https://github.com/ACROSS-Team/across-server/commit/0b0182f7d53db1912a6901f08ccb116db420a478))


### Documentation

* adjust issue templates to follow yaml syntax ([8b2e810](https://github.com/ACROSS-Team/across-server/commit/8b2e8105748a1f6e43c51aa252ac73b8fea333a2))
* adjust ticket template to include more granular sections ([65e39d1](https://github.com/ACROSS-Team/across-server/commit/65e39d14d949a852b02fb77f31ceaec2d7193096))


### Miscellaneous Chores

* delete create role route ([e7a7a33](https://github.com/ACROSS-Team/across-server/commit/e7a7a33b734425294a916793f391fbf3aca112cd))
* delete create role route ([#288](https://github.com/ACROSS-Team/across-server/issues/288)) ([e7a7a33](https://github.com/ACROSS-Team/across-server/commit/e7a7a33b734425294a916793f391fbf3aca112cd))
