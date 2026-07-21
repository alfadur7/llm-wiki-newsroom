---
layout: default
title: LLM Wiki Newsroom
permalink: /ko/
lang: ko
description: >-
  흩어진 문서를 서로 연결된 마크다운 위키로 정리해 주는 멀티에이전트 'AI 편집국'.
  글 쓰는 에이전트와 검수하는 에이전트를 아예 따로 둡니다. 로컬 우선, 순수 마크다운 + git,
  RAG의 구조화된 대안.
software_schema: true
schema_inlanguage: ko
schema_url: "https://alfadur7.github.io/llm-wiki-newsroom/ko/"
schema_description: >-
  흩어진 문서를 서로 연결된 마크다운 위키로 정리해 주는 멀티에이전트 'AI 편집국'
  프레임워크. 글을 쓰는 에이전트와 검수하는 에이전트를 아예 따로 두고, 위키를 만드는
  저작 지침이 스스로 조금씩 나아진다. 로컬 우선, 순수 마크다운과 git, RAG의 구조화된 대안.
schema_keywords: "LLM 위키, 카파시 LLM Wiki, RAG 대안, 멀티에이전트, Claude Code, 지식베이스, 세컨드 브레인, 옵시디언, 모순 추적, 자기진화 지침, 로컬 우선"
hreflang_en: "https://alfadur7.github.io/llm-wiki-newsroom/"
hreflang_ko: "https://alfadur7.github.io/llm-wiki-newsroom/ko/"
---

*In [English]({{ '/' | relative_url }}).*

**LLM Wiki Newsroom은 흩어진 문서를 서로 연결된, 사람이 읽을 수 있는 마크다운 위키로 정리해 주는 오픈소스 프레임워크입니다.** 신문사 편집국을 본떠 다섯 역할로 나눈 'AI 편집국'이 그 일을 맡습니다. 기사·메모·PDF를 폴더에 넣고 명령어 하나만 실행하면, [Claude Code](https://www.anthropic.com/claude-code) 기반 에이전트가 문서를 읽고 인물·개념·관계를 뽑아 서로 링크된 페이지로 엮습니다. RAG처럼 질문할 때마다 원문을 다시 긁어모으는 대신, 지식을 미리 구조화해 쌓아 둡니다. 여느 구현과 크게 다른 점이 둘 있습니다. 글 쓰는 에이전트와 검수하는 에이전트를 아예 따로 뒀고, 위키를 만드는 저작 지침이 스스로 조금씩 나아집니다.

[GitHub에서 보기 »](https://github.com/alfadur7/llm-wiki-newsroom){: .btn }
[FAQ 읽기 »]({{ '/ko/faq/' | relative_url }}){: .btn }

## 설치 전에 결과부터 보기

레포에 들어 있는 예제('AI에서 오픈소스란 무엇인가' 논쟁)는 바로 볼 수 있는 **[GitHub Wiki](https://github.com/alfadur7/llm-wiki-newsroom/wiki)**로 공개돼 있습니다. clone 없이도 생성된 페이지를 둘러볼 수 있어요. 아래 인터랙티브 지식 그래프는 clone 후 로컬에서 돕니다.

[![인터랙티브 지식 그래프. 페이지는 노드, 위키링크는 엣지, 비슷한 주제끼리 자동으로 색깔별로 묶임]({{ '/knowledge-graph.png' | relative_url }})](https://github.com/alfadur7/llm-wiki-newsroom/wiki)

*인터랙티브 그래프(`graph/graph.html`)입니다. 페이지는 노드, 위키링크는 엣지로 그리고, 자동으로 감지한 클러스터(비슷한 주제끼리 묶은 무리)별로 색을 입힙니다. 여기에 물리 시뮬레이션 배치와 필터·검색이 들어 있어요. 규모감을 보여드리려고 더 큰 비공개 인스턴스(약 2,300노드) 화면을 실었지만, 이 레포는 똑같은 방식으로 둘러볼 수 있는 노드 15개짜리 작은 예제를 담고 있습니다.*

## 무엇이 다른가

이제 [카파시의 LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 아이디어를 구현한 것은 많습니다. 인기 있는 구현들을 읽어 보고 나니, 여기서 정말 드문 건 세 가지였습니다.

- **저작 지침이 스스로 진화합니다.** 같은 지적이 반복되면 시스템이 자기 저작 규칙을 스스로 고칩니다. 단, 바꾸기 전과 후를 어느 쪽이 바뀐 버전인지 모르게 나란히 비교해서, 실제로 점수가 오를 때만 그 변경을 남깁니다. 이때 검증에는 개선에 한 번도 안 쓴 새 실패 사례만 써서, 규칙이 같은 시험 문제에만 익숙해지는 것(overfit)을 막습니다. 늘 처음 보는 사례로 확인하는 셈이죠. 그래서 위키만 좋아지는 게 아니라, 위키를 만드는 규칙도 같이 좋아집니다. *(아직 실험 단계라, 정말 값을 하는지 측정하는 중이지 "풀었다"고 주장하진 않습니다.)*
- **에이전트 하나가 아니라 편집국 전체입니다.** 기자·칼럼니스트·데스크(검수)·교열·편집장 다섯 역할로 일을 나눴습니다. 그런데 멀티에이전트라고 다 알아서 판단하는 건 아니에요. **LLM이 독립적으로 판단하는 자리는 데스크(검수) 하나뿐**이고, 나머지는 성격이 다른 글쓰기 작업이거나, LLM이 아니라 규칙대로 도는 파이썬 검사(린트), 작업을 잇는 조율(오케스트레이션)입니다. 검수하는 데스크는 완성된 초안과 채점 기준만 보고, 글쓴이가 무슨 생각으로 썼는지는 못 봅니다. 핵심은 에이전트 개수가 아니라 이 컨텍스트 격리입니다.
- **메멕스식 연상 탐색.** 저장해 둔 읽기 경로(trail)와 "뜻밖의 연결"을 찾아 주는 기능입니다. [1945년 바네바 부시가 구상한 Memex](https://en.wikipedia.org/wiki/Memex)(연결형 정보 기계)에서 따왔고, 다른 구현엔 없는 부분입니다.

나머지, 그러니까 지식 그래프·모순 추적·연쇄 갱신·순수 마크다운/옵시디언 출력은 다른 LLM 위키 도구도 어떤 형태로든 갖고 있습니다. 자기진화 지침, 채점 기준을 갖춘 다섯 역할 편집국, 메멕스 탐색이 이 프로젝트가 거는 승부수입니다.

## RAG와 어떻게 다른가

|  | RAG | LLM Wiki Newsroom |
|---|---|---|
| 지식 상태 | 질문마다 다시 추출 | 한 번 정리해 계속 갱신 |
| 검색 단위 | 소스 조각 | 구조화된 위키 페이지 |
| 상호 참조 | 없음 | 위키링크 + 백링크 색인 |
| 모순 처리 | 질문 시점에 드러날 수 있음 | 문서를 넣을 때 표시하고 추적 |
| 축적 효과 | 없음 | 새 소스가 기존 페이지를 보강 |
| 탐색 | 키워드 검색 | 그래프 순회 + 연상 경로(trail) |

## 핵심 기능

- **지속되는 순수 마크다운 지식베이스.** 버전관리되는 `.md` 파일로 쌓이는 "제2의 뇌"입니다. 특정 서비스에 갇히지 않고, [옵시디언](https://obsidian.md) 볼트로도 그대로 씁니다.
- **연쇄 갱신.** 문서 하나를 넣으면 관련된 기존 페이지 10~15개가 알아서 갱신됩니다.
- **모순 추적.** 소스끼리 안 맞는 주장은 질문할 때가 아니라 문서를 넣는 순간 표시됩니다.
- **인터랙티브 지식 그래프.** 페이지는 노드, 링크는 엣지로 그리고, 자동으로 묶어 브라우저에서 둘러봅니다.
- **연상 탐색(Memex).** 연결된 개념을 따라가며 뜻밖의 관계를 드러냅니다.
- **로컬 우선.** 그래프·린트·검색 파이썬 도구는 외부 API 키 없이 내 컴퓨터에서 돕니다. 다만 에이전트 자체는 Claude Code로 돌아가니, 그건 각자 자기 키를 물려 씁니다(BYOK).

## 빠른 시작

```bash
git clone https://github.com/alfadur7/llm-wiki-newsroom.git
cd llm-wiki-newsroom
```

또는 **["Use this template"](https://github.com/alfadur7/llm-wiki-newsroom/generate)** 로 내 위키 레포를 바로 만들 수 있습니다. 그런 다음 `/wiki-ingest`로 내 소스를 넣으면 됩니다. 자세한 설치, 아홉 개 슬래시 명령어, 구조는 **[README(영문)](https://github.com/alfadur7/llm-wiki-newsroom#readme)** 에 있습니다.

## 더 알아보기

- **[README(영문)](https://github.com/alfadur7/llm-wiki-newsroom#readme)**: 설치, 명령어, 구조, 기능 레퍼런스
- **[FAQ(한국어)]({{ '/ko/faq/' | relative_url }})**: 자주 묻는 질문
- **[예제 위키 둘러보기](https://github.com/alfadur7/llm-wiki-newsroom/wiki)**: 레포에 담긴 예제, clone 불필요
- **[카파시의 원본 LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)**: 설계 영감

---

*MIT 라이선스. LLM Wiki 패턴을 구조화하고 로컬 우선으로 풀어낸 구현입니다. 공개된 채로 만들고 다듬고 있습니다.*
