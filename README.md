# Workbench Pages

이 저장소는 [작업대](https://busyzeus.github.io/workbench/)를 GitHub Pages에 배포합니다. 앱 소스는 비공개 `workbench-src` 저장소에서 관리합니다.

1. 소스 작업 폴더에서 `npm run build:pages`로 빌드하고 `deploy/README.md`의 절차대로 배포 묶음과 SHA-256 파일을 만듭니다.
2. 공개 저장소의 같은 GitHub Release에 `workbench-pages.tar.gz`와 `workbench-pages.tar.gz.sha256`을 첨부합니다. GitHub의 Git 파일 크기 제한을 넘는 엔진이 들어 있으므로 압축 파일은 Release 자산으로 올립니다.
3. 저장소의 **Settings → Pages → Source**를 **GitHub Actions**로 지정합니다.
4. **Actions → Publish Workbench to GitHub Pages → Run workflow**에서 해당 릴리스 태그를 입력합니다.

워크플로가 릴리스 자산의 SHA-256과 사이트 경로를 확인한 뒤 `/workbench/`에 배포합니다.
