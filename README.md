# Zack-Zack-<span style="color: red">Deutsch</span> (backend)

![readme_stripe.svg](docs/images/readme_stripe.svg)

![Build and Test](https://github.com/zola8/zack-zack-deutsch-be/actions/workflows/build.yml/badge.svg)

#### Prod URLs

- https://zack-zack-deutsch-fe.vercel.app
- https://zack-zack-deutsch-be.vercel.app/docs

## 1. Installation

#### Prerequisites

- Python 3.13+

#### Install dependencies

```shell
pip install -r requirements.txt
```

## 2. Check your limits

#### DeepL

- web: https://www.deepl.com/en/your-account/usage
- One-time credit of 1 million characters

#### Azure

- web: https://portal.azure.com/#home
- 2 million characters of any combination of standard translation and custom translation training free per month

#### Vercel

- FE: https://vercel.com/zola8s-projects/zack-zack-deutsch-fe
- BE: https://vercel.com/zola8s-projects/zack-zack-deutsch-be

#### Postgres

- Postgres console: https://console.aiven.io/account/a5e0f2593af3/project/zola8/services/zz-deutsch-postgres/overview

    ```
    postgres://<USER>:<PASSWORD>@zz-deutsch-postgres-zola8.h.aivencloud.com:25212/defaultdb?sslmode=require
    ```
