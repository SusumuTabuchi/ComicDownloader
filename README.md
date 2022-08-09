<h1 align="center" style="border-bottom: none">
    <b>
        <a href="https://affine.pro">AFFiNE.PRO</a><br>
    </b>
    The Next-Gen Knowledge Base to Replace Notion & Miro.
    <br>
</h1>

<p align="center">
Planning, Sorting and Creating all Together. Open-source, Privacy-First, and Free to use.
</p>

<div align="center">

<!--
Make New Badge Pattern badges inline
See https://github.com/all-?/all-contributors/issues/361#issuecomment-637166066
-->
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->

[all-contributors-badge]: https://img.shields.io/badge/all_contributors-11-orange.svg?style=flat-square

<!-- ALL-CONTRIBUTORS-BADGE:END -->

<!-- [![All Contributors][all-contributors-badge]](#contributors)
[![Node](https://img.shields.io/badge/node->=16.0-success)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/TypeScript-4.7-3178c6)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-18-61dafb)](https://reactjs.org/)
[![Rust](https://img.shields.io/badge/Rust-1.62-dea584)](https://www.rust-lang.org/) -->

</div>

<!-- <p align="center">
    <a href="http://affine.pro"><b>Website</b></a> •
    <a href="https://discord.com/invite/yz6tGVsf5p"><b>Discord</b></a> •
    <a href="https://twitter.com/AffineOfficial"><b>Twitter</b></a> •
    <a href="https://medium.com/@affineworkos"><b>Medium</b></a> •
    <a href="https://t.me/affineworkos"><b>Telegram</b></a>
</p>

<p align="center"><img width="1920" alt="affine_screen" src="https://user-images.githubusercontent.com/21084335/182552060-972cac0e-6258-4ccb-85bd-3bb466c30ccd.png"><p/>

# Stay Up-to-Date and Support Us

![952cd7a5-70fe-48ab-b74f-23981d94d2c5](https://user-images.githubusercontent.com/79301703/182365526-df074c64-cee4-45f6-b8e0-b912f17332c6.gif) -->

# How to use

Jenkins有効化
-   コンテナの立ち上げ後、Jenkinsコンテナに入り「copy_sshkey.sh」を実行する
    -   パスワード入力を求められた場合、APPコンテナのJenkinsユーザーパスワードを入力する
    -   「Are you sure you want to continue connecting (yes/no/[fingerprint])?」に対しては「yes」
    -   「ERROR: ssh: connect to host comic_app port 22: Connection refused」が表示される場合はAppコンテナでsshdが立ち上がっていないので立ち上げておく
-   Appコンテナに入り、「setting_sshkey.sh」を実行する
    -   Passwordを求めらたらjenkinsユーザーのパスワードを入力する
-   JenkinsをWEBブラウザで開き、初期設定をする
-   Jenkins管理画面でSSH認証情報の設定をする
    -   Jenkinsの管理＞Manage Credentials
        -   「global」のドメインをクリック
        -   「認証情報の追加」をクリック
        -   認証情報の内容を入力する
            -   種類：SSHユーザー名と秘密鍵
            -   スコープ：グローバル
            -   ID：jenkins
            -   説明：適当でOK
            -   ユーザー名：jenkins
            -   秘密鍵：直接入力で「Add」ボタンをクリック
                -   Jenkinsコンテナの「/var/jenkins_home/.ssh/id_rsa」を全てコピーして貼り付ける
                    ※「-----BEGIN　＊＊＊」から全て
            -   パスフレーズ：秘密鍵ファイル作成時に設定したパスフレーズ（設定していれば）
    -   Jenkins管理画面で管理ノードに外部サーバを追加
        -   「ノードの管理」をクリック
        -   新規ノード作成　をクリック
        -   ノード名にホスト名を入力して、「Permanent Agent」を選択して「OK」をクリック
            ホスト名はAppコンテナ名
        -   管理対象サーバの情報を入力
            -   ノード名：ホスト名
            -   説明：適当でOK
            -   リモートFSルート：Appコンテナのjenkinsユーザーのホームディレクトリ
            -   ラベル：ホスト名と同じでOK
            -   用途：このマシーンを特定ジョブ専用にする
            -   起動方法：SSH経由でUnixマシンのスレーブエージェントを起動
            -   ホスト：ホスト名
            -   認証情報：前の手順で作成しておいたSSH秘密鍵認証を選択
            -   Host Key Verification Strategy：Known hosts file Verification Strategy
            -   可用性：Keep this agent online as much as possible
        -   「保存」ボタンをクリック
    -   JOBでノードを設定する
        -   「実行するノードを制限」でラベルを設定

<!-- If you have experience in front-end development, please [refer to here](https://affine.gitbook.io/affine/basic-documentation/contribute-to-affine); if you want to experience our latest version, please wait a moment, we will launch a web version in the near future.
And, thanks to Lee who [made a desktop build with Tauri](https://github.com/m1911star/affine-client) for you to try out.
Please notice that AFFiNE is still under Alpha stage and is not ready for production use. -->

# Table of contents

<!-- -   [Stay Up-to-Date and Support Us](#stay-up-to-date-and-support-us)
-   [How to Use](#how-to-use)
-   [Table of contents](#table-of-contents)
    -   [Shape your page](#shape-your-page)
    -   [Plan your task](#plan-your-task)
    -   [Sort your knowledge](#sort-your-knowledge)
    -   [Create your story](#create-your-story)
-   [Documentation](#documentation)
    -   [Getting Started with development](#getting-started-with-development)
-   [Roadmap](#roadmap)
-   [Releases](#releases)
-   [Feature requests](#feature-requests)
-   [FAQ](#faq)
-   [The Philosophy of AFFiNE](#the-philosophy-of-affine)
-   [Community](#community)
-   [Contributors](#contributors)
-   [Acknowledgments](#acknowledgments)
-   [License](#license) -->

## Shape your page

<!-- ![546163d6-4c39-4128-ae7f-55d59bc3b76b](https://user-images.githubusercontent.com/79301703/182365611-b0ba3690-21c0-4d9b-bfbc-0bc15da05aeb.gif) -->

## Plan your task

<!-- ![41a7b3a4-32f2-4d18-ac6b-57d1e1fda753](https://user-images.githubusercontent.com/79301703/182366553-1f6558a7-f17b-4611-ab95-aea3ec997154.gif) -->

## Sort your knowledge

<!-- ![c9e1ff46-cec2-411b-b89d-6727a5e6f6c3](https://user-images.githubusercontent.com/79301703/182366602-08e44d28-a031-4097-9904-52fb9b1e9e17.gif) -->

## Create your story

<!-- We want your data always to be yours, and we don't want to make any sacrifice to your accessibility. Your data is always local-stored first, yet we support real-time collaboration on a peer-to-peer basis. We don't think "privacy-first" is a good excuse for not supporting modern web features.
Collaboration isn't only necessary for teams -- you may take and insert pics on your phone, then edit them on your desktop, and share them with your collaborators.
Affine is fully built with web technologies so that consistency and accessibility are always guaranteed on Mac, Windows and Linux. The local file system support will be available when version 0.0.1beta is released. -->

# Documentation

<!-- AFFiNE is not yet ready for production use. To install, you may check how to build or deploy the AFFiNE in [quick-start](https://affine.gitbook.io/affine/basic-documentation/contribute-to-affine/quick-start). For the full documentation, please view it [here](https://affine.gitbook.io/affine/). -->

## Getting Started with development

<!-- Please view the path Contribute-to-AFFiNE/Software-Contributions/Quick-Start in the documentation. -->

# Roadmap

<!-- Coming Soon... -->

# Releases

<!-- Get our latest [release notes](https://github.com/toeverything/AFFiNE/wiki) from here. -->

# Feature requests

<!-- Please go to [Feature request](https://github.com/toeverything/AFFiNE/issues). -->

# FAQ

Jenkinsが接続できない
-   Appコンテナの「.ssh/known_hosts」を開き、テキストを全て削除してみる
    マウントしているフォルダにあるので、2回目以降のビルド時に問題が起こる場合がある
<!-- Get quick help on [Telegram](https://t.me/affineworkos) and [Discord](https://discord.gg/yz6tGVsf5p) along with other developers and contributors.

Latest news and technology sharing on [Twitter](https://twitter.com/AffineOfficial), [Medium](https://medium.com/@affineworkos) and [AFFiNE Blog](https://blog.affine.pro/). -->

# The Philosophy of AFFiNE

<!-- Timothy Berners-Lee once taught us about the idea of the semantic web, where all the data can be interpreted in any form while the "truth" is kept. This gives our best image of an ideal knowledge base by far, that sorting of information, planning of project and goals as well as creating of knowledge can be all together.
We have witnessed waves of paradigm shift so many times. At first, everything was noted on office-like apps or DSL like LaTeX, then we found todo-list apps and WYSIWYG markdown editors better for writing and planning. Finally, here comes Notion and Miro, who take advantage of the idea of blocks to further liberate our creativity.
It is all perfect... If there are not so many waste operations and redundant information. And, we insist that privacy first should always be given by default.
That's why we are making AFFiNE. Some of the most important features are:

-   Transformable
    -   Every block can be transformed equally well as a database
        -   e.g. you can now set up a to-do with MarkDown in text view and edit it in kanban view.
    -   Every doc can be turned into a whiteboard
        -   An always good-to-read, structured docs-form page is the best for your notes, but a boundless doodle surface is better for collaboration and creativity.
-   Atomic
    -   The basic element of affine are blocks, not pages.
        -   Blocks can be directly reused and synced between pages.
    -   Pages and blocks are searched and organized based on connected graphs, not tree-like paths.
    -   Dual-link and semantic search are fully supported.
-   Collaborative and privacy-first
    -   Data is always stored locally by default
    -   CRDTs are applied so that peer-to-peer collaboration is possible.

We really appreciate the idea of Monday, Airtable and Notion databases. They inspired what we think is right for task management. But we don't like the repeated works -- we don't want to set a todo easily with markdown but end up re-write it again in kanban or other databases.
With AFFiNE, every block group has infinite views, for you to keep your single source of truth.

We would like to give special thanks to the innovators and pioneers who greatly inspired us:

-   Quip & Notion -- that docs can be organized as blocks
-   Taskade & Monday -- brilliant multi-dimensional tables
-   Height & Linear -- beautiful task management tool

We would also like to give thanks to open-source projects that make affine possible:

-   [Yjs](https://github.com/yjs/yjs) & [Yrs](https://github.com/y-crdt/y-crdt) -- Fundamental support of CRDTs for our implementation on state management and data sync.
-   [React](https://github.com/facebook/react) -- View layer support and web GUI framework.
-   [Rust](https://github.com/rust-lang/rust) -- High performance language that extends the ability and availability of our real-time backend, JWST.
-   [Fossil](https://www2.fossil-scm.org/home/doc/trunk/www/index.wiki) -- Source code management tool made with CRDTs which inspired our design on block data structure.
-   [slatejs](https://github.com/ianstormtaylor/slate) -- Customizable rich-text editor.
-   [Jotai](https://github.com/pmndrs/jotai) -- Minimal state management tool for frontend.
-   [Tldraw](https://github.com/tldraw/tldraw) -- Excellent drawing board.
-   [MUI](https://github.com/mui/material-ui) -- Our most used graphic UI component library.
-   Other [dependencies](https://github.com/toeverything/AFFiNE/network/dependencies)

Thanks a lot to the community for providing such powerful and simple libraries, so that we can focus more on the implementation of the product logic, and we hope that in the future our projects will also provide a more easy-to-use knowledge base for everyone. -->

# Community

For help, discussion about best practices, or any other conversation that would benefit from being searchable:

<!-- [Discuss AFFiNE on GitHub](https://github.com/toeverything/AFFiNE/discussions) -->

# Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<!-- <table>
  <tr>
    <td align="center"><a href="https://darksky.eu.org/"><img src="https://avatars.githubusercontent.com/u/25152247?v=4?s=100" width="100px;" alt=""/><br /><sub><b>DarkSky</b></sub></a><br /><a href="https://github.com/toeverything/AFFiNE/commits?author=darkskygit" title="Code">💻</a> <a href="https://github.com/toeverything/AFFiNE/commits?author=darkskygit" title="Documentation">📖</a></td>
    <td align="center"><a href="http://zhangchi.page/"><img src="https://avatars.githubusercontent.com/u/5910926?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Chi Zhang</b></sub></a><br /><a href="https://github.com/toeverything/AFFiNE/commits?author=tzhangchi" title="Code">💻</a> <a href="https://github.com/toeverything/AFFiNE/commits?author=tzhangchi" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/alt1o"><img src="https://avatars.githubusercontent.com/u/21084335?v=4?s=100" width="100px;" alt=""/><br /><sub><b>wang xinglong</b></sub></a><br /><a href="https://github.com/toeverything/AFFiNE/commits?author=alt1o" title="Code">💻</a> <a href="https://github.com/toeverything/AFFiNE/commits?author=alt1o" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/DiamondThree"><img src="https://avatars.githubusercontent.com/u/24630517?v=4?s=100" width="100px;" alt=""/><br /><sub><b>DiamondThree</b></sub></a><br /><a href="https://github.com/toeverything/AFFiNE/commits?author=DiamondThree" title="Code">💻</a> <a href="https://github.com/toeverything/AFFiNE/commits?author=DiamondThree" title="Documentation">📖</a></td>
    <td align="center"><a href="https://lawvs.github.io/profile/"><img src="https://avatars.githubusercontent.com/u/18554747?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Whitewater</b></sub></a><br /><a href="https://github.com/toeverything/AFFiNE/commits?author=lawvs" title="Code">💻</a> <a href="https://github.com/toeverything/AFFiNE/commits?author=lawvs" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/zuoxiaodong0815"><img src="https://avatars.githubusercontent.com/u/53252747?v=4?s=100" width="100px;" alt=""/><br /><sub><b>xiaodong zuo</b></sub></a><br /><a href="https://github.com/toeverything/AFFiNE/commits?author=zuoxiaodong0815" title="Code">💻</a> <a href="https://github.com/toeverything/AFFiNE/commits?author=zuoxiaodong0815" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/SaikaSakura"><img src="https://avatars.githubusercontent.com/u/11530942?v=4?s=100" width="100px;" alt=""/><br /><sub><b>MingLIang Wang</b></sub></a><br /><a href="https://github.com/toeverything/AFFiNE/commits?author=SaikaSakura" title="Code">💻</a> <a href="https://github.com/toeverything/AFFiNE/commits?author=SaikaSakura" title="Documentation">📖</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/QiShaoXuan"><img src="https://avatars.githubusercontent.com/u/22772830?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Qi</b></sub></a><br /><a href="https://github.com/toeverything/AFFiNE/commits?author=QiShaoXuan" title="Code">💻</a> <a href="https://github.com/toeverything/AFFiNE/commits?author=QiShaoXuan" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/mitsuhatu"><img src="https://avatars.githubusercontent.com/u/110213079?v=4?s=100" width="100px;" alt=""/><br /><sub><b>mitsuhatu</b></sub></a><br /><a href="https://github.com/toeverything/AFFiNE/commits?author=mitsuhatu" title="Code">💻</a> <a href="https://github.com/toeverything/AFFiNE/commits?author=mitsuhatu" title="Documentation">📖</a></td>
    <td align="center"><a href="https://shockwave.me/"><img src="https://avatars.githubusercontent.com/u/15013925?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Austaras</b></sub></a><br /><a href="https://github.com/toeverything/AFFiNE/commits?author=Austaras" title="Code">💻</a> <a href="https://github.com/toeverything/AFFiNE/commits?author=Austaras" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/uptonking?tab=repositories&type=source"><img src="https://avatars.githubusercontent.com/u/11391549?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Jin Yao</b></sub></a><br /><a href="https://github.com/toeverything/AFFiNE/commits?author=uptonking" title="Code">💻</a> <a href="https://github.com/toeverything/AFFiNE/commits?author=uptonking" title="Documentation">📖</a></td>
  </tr>
</table> -->

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

# License

<!-- AFFiNE is distributed under the terms of MIT license.

See LICENSE for details. -->