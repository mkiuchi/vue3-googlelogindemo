# Sign in with Google (aka. Google Identity Service) を Vue3 から使う

[Google Sign-In](https://developers.google.com/identity) が[非推奨になり、2023 年 3 月 31 日のサポート終了日以降はダウンロードできなくなる](https://developers.googleblog.com/2021/08/gsi-jsweb-deprecation.html)。新しいのは [Google Identity Service](https://developers.google.com/identity/oauth2/web) と呼ばれ、 [Sign In With Google](https://developers.google.com/identity/gsi/web) というブランドになっているようだ。

で、これを使って Vue3 の SPI アプリケーションを作ってみようとやってみたので記録を残しておく

この記事で使用しているサンプルの全体は https://github.com/mkiuchi/vue3-googlelogindemo/ から取得することができる

# 1. この手順の制約

- 1日あたりのトークン付与は上限 10,000 。[上限緩和も可能](https://support.google.com/code/contact/oauth_quota_increase)
    - 参考: https://support.google.com/cloud/answer/9028764
    - 具体的に何のトークン付与なのかが書かれていないので、いろいろ推測ができるが
        - 仮にアクセストークンも含めて上限 10,000 だとしたら、1ユーザ1日 あたり少なくとも 49 トークン (24 アクセストークン、24 ID トークン、1 リフレッシュトークン) 付与されるので、利用できるユーザ上限は 10000 ÷ 49 = 204 人となる。
        - 最初の認証だけカウントされるのであれば 10,000 に近いくらいのユーザを収容できる

# 2. Vue3 で Sign In With Google を使うには

[vue3-google-loginライブラリ](https://www.npmjs.com/package/vue3-google-login)を使えばいい。

## 2.1. 前提条件
- 認証するユーザは [Cloud Identity](https://cloud.google.com/identity) のユーザ
    - かつ、対象の GCP プロジェクトのユーザとして追加されている
- GCP上で OAuth同意画面、OAuth 2.0 クライアント IDを作成した
    - OAuth 同意画面の設定値
        - ユーザの種類: [内部](https://support.google.com/cloud/answer/10311615#zippy=%2Cinternal)
    - OAuth 2.0 クライアント ID の設定値
        - 名前: 任意の名前
        - 承認済みのJavascript生成元
            - URL1: http://localhost
            - URL2: http://localhost:8080
        - 承認済みのリダイレクトURI
            - URL1: http://localhost:8080

## 2.2. インストールと初期化

```shell
npm install --save vue3-google-login
```

初期化

```javascript:@/src/main.js
import vue3GoogleLogin from 'vue3-google-login'
createApp(App)
  .use(vue3GoogleLogin, {
    clientId: // クライアントID,
    scope: 'email profile openid'
  })
  .mount('#app')

```

## 2.3. Log in with Google ボタンの表示

2 種類の方法があり、それぞれログイン成功時の挙動が変わる。

### 2.3.1. デフォルト

この設置方法だと、ログイン成功時には クレデンシャル(=ID トークン) が戻ってくる。

参考: https://yobaji.github.io/vue3-google-login/#googlelogin-component

```html:@/src/components/LoginDialog1.vue
<GoogleLogin :callback="callback"/>
```

```javascript:@/src/components/LoginDialog1.vue
export default {
    name: 'LoginDialog1',
    setup() {
        const callback = async (response) => {
            console.log("Login response", response)
        }
        return {
            callback
        }
    }
}
```

### 2.3.2. カスタム

この設置方法だと、ログイン成功時には 認証コード が戻ってくる。

参考: https://yobaji.github.io/vue3-google-login/#custom-login-button

認証コードは APIサーバ(not Google)に渡して、ID トークン、リフレッシュトークン、アクセストークンに交換することができる。

```html:@/src/components/LoginDialog2.vue
<GoogleLogin :callback="callback">
    <v-btn style="height:55px;width:210px">
        <img src="/assets/btn_google_signin_light_normal_web@2x.png"  style="height:50px"/>
    </v-btn>
</GoogleLogin>
```

```javascript:@/src/components/LoginDialog2.vue
export default {
    name: 'LoginDialog2',
    setup() {
        const callback = async (response) => {
            console.log("Login response", response)
        }
        return {
            callback
        }
    }
}
```

## 2.4. 認証後の情報を検証する

### 2.4.1. クレデンシャル(=IDトークン)を検証し、プロファイル情報を戻す

デフォルトの設置方法で、戻り値にクレデンシャル(=ID トークン)を得た場合、APサーバ側はこんな感じにする。ID トークンを検証し、検証が成功したらプロフィール情報を戻す。

参考: https://developers.google.com/identity/gsi/web/guides/verify-google-id-token

この方法で取れているのはクレデンシャル(=ID トークン)なので、ここから更新トークンやアクセストークンを取得する方法はない。

```python:app.py
import json
import requests as rq
from urllib.parse import quote
from flask import Flask, jsonify, make_response, request, abort
from flask_cors import CORS, cross_origin
from google.oauth2 import id_token
from google.auth.transport import requests
app = Flask(__name__)
CORS(app)

client_id = "863627961660-os8jlqp8h84240m81rsfo0tts0th2ijs.apps.googleusercontent.com"

@app.route('/auth/google/verifycredential', methods=['POST'])
def verifyCredential():    # クレデンシャル(=IDトークン)を検証し、プロファイル情報を戻す
    # https://developers.google.com/identity/gsi/web/guides/verify-google-id-token
    authcode = request.headers["Authorization"][7:]
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(
            authcode, requests.Request(), client_id)
        return make_response(jsonify(idinfo), 200)
    except BaseException as e:
        # Invalid token
        return make_response(jsonify({"reason": str(e)}), 403)
```

リクエスト側(ブラウザ)はこんな感じに呼び出す。

```javascript:@/src/components/LoginDialog1.vue
export default {
    name: 'LoginDialog1',
    setup() {
        const callback = async (response) => {
            console.log("Login response", response)
            await fetch(
                'http://localhost:5000/auth/google/verifyauthcredential',
                {
                    method: 'POST',
                    headers: {
                        'Authorization': 'Bearer ' + response.credential,
                        'Content-Type': 'application/json'
                    }
                }
            ).then((r) => {
                console.log('response header', r)
                r.text()
                    .then((t) => {
                        console.log('response', JSON.parse(t))
                    })
            })
        }
        return {
            callback
        }
    }
}
```

### 2.4.2. 認証コードを検証し、アクセストークン、リフレッシュトークン、ID トークンを戻す

戻り値に認証コードを得た場合、その認証コードを AP サーバに渡し、APサーバは認証コードを検証し、検証が成功したらアクセストークン、リフレッシュトークン、ID トークンを戻す。

参考: https://developers.google.com/identity/protocols/oauth2/web-server#exchange-authorization-code

リダイレクトURI が認証コードを取得したURIと一致しないと検証が成功しないので注意する。

ここで提供されるアクセストークンの有効時間は 3600 秒(=1 時間)。変更はできない。リフレッシュトークンの有効期限はない。

```python
import json
import requests as rq
from urllib.parse import quote
from flask import Flask, jsonify, make_response, request, abort
from flask_cors import CORS, cross_origin
app = Flask(__name__)
CORS(app)

@app.route('/auth/google/verifyauthcode', methods=['POST'])
@cross_origin(supports_credentials=True, methods=['POST'], origin="http://localhost:8080")
def verifyAuthCode():
    # 認証コードから、更新トークンとアクセストークンを取得する
    # https://developers.google.com/identity/protocols/oauth2/web-server#exchange-authorization-code
    authcode = request.headers["Authorization"][7:]
    url = "https://oauth2.googleapis.com/token"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'charset': "UTF-8"
    }
    content = 'code=' + authcode
    content += '&client_id=クライアントID'
    content += '&client_secret=クライアントシークレット'
    content += '&redirect_uri=' + quote('http://localhost:8080')
    content += '&grant_type=authorization_code'

    r = rq.post(url, data=content, headers=headers)
    if r.status_code != 200:
        abort(403, description=r.text)
    body = json.loads(r.text)
    print(body)
    # トークンを Set-Cookie ヘッダにセットして返信する（これは脆弱性のある方法なので推奨できない）
    ret = make_response(jsonify({"expires_in": body["expires_in"]}))
    ret.headers.add("Set-Cookie", "access_token="+body["access_token"]+"; SameSite=None; Max-Age=86400; HttpOnly; Secure; Path=/")
    ret.headers.add("Set-Cookie", "refresh_token="+body["refresh_token"]+"; SameSite=None; Max-Age=31536000; HttpOnly; Secure; Path=/")
    ret.headers.add("Set-Cookie", "id_token="+body["id_token"]+"; SameSite=None; Max-Age=86400; HttpOnly; Secure; Path=/")
    return ret, 200
```

リクエスト側(ブラウザ)はこんな感じに呼び出す。

```javascript:@/src/components/LoginDialog2.vue
import { useRouter } from 'vue-router'

export default {
    name: 'LoginDialog2',
    setup() {
        const router = useRouter()
        const callback = async (response) => {
            await fetch(
                'http://localhost:5000/auth/google/verifyauthcode',
                {
                    method: 'POST',
                    mode: 'cors',
                    credentials: 'include',
                    headers: {
                        'Authorization': 'Bearer ' + response.code,
                        'Content-Type': 'application/json'
                    }
                })
                .then((r) => {
                    console.log('auth code successfully verified')
                    console.log('response status', r.status, r.statusText)
                    r.text()
                        .then((t) => {
                            // 成功したらメインページにリダイレクト
                            console.log('200 response', JSON.parse(t))
                            router.push({'name': 'MainPage'})
                        })
                })
                .catch((e) => {
                    console.log('auth code verify failed')
                    console.log('response status', e.status, e.statusText)
                })
        }
        return {
            callback
        }
    }
}
```

## 2.5. どちらの方法がいいのか?

ここまで読んでくるとわかると思うが、"[2.3.1. デフォルト](#231-%E3%83%87%E3%83%95%E3%82%A9%E3%83%AB%E3%83%88)" + "[2.4.1. クレデンシャル(=IDトークン)を検証し、プロファイル情報を戻す](#241-%E3%82%AF%E3%83%AC%E3%83%87%E3%83%B3%E3%82%B7%E3%83%A3%E3%83%ABid%E3%83%88%E3%83%BC%E3%82%AF%E3%83%B3%E3%82%92%E6%A4%9C%E8%A8%BC%E3%81%97%E3%83%97%E3%83%AD%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E6%83%85%E5%A0%B1%E3%82%92%E6%88%BB%E3%81%99)" の方式で ID トークンだけ取得しても、ID トークン自体の有効期限が 3,600秒(=1時間) で延長するすべがない。ドキュメントにも書いてあるが、[何かしらのサービスへのアクセスを行う場合にはアクセストークン、リフレッシュトークンへの交換を行う必要があり](https://developers.google.com/identity/protocols/oauth2#2.-obtain-an-access-token-from-the-google-authorization-server.)、アクセストークン、リフレッシュトークンを使えば 3,600秒 を超えた連続使用も可能となる。

以降は "[2.3.2. カスタム](#232-%E3%82%AB%E3%82%B9%E3%82%BF%E3%83%A0)" + "[2.4.2. 認証コードを検証し、アクセストークン、リフレッシュトークン、ID トークンを戻す](#242-%E8%AA%8D%E8%A8%BC%E3%82%B3%E3%83%BC%E3%83%89%E3%82%92%E6%A4%9C%E8%A8%BC%E3%81%97%E3%82%A2%E3%82%AF%E3%82%BB%E3%82%B9%E3%83%88%E3%83%BC%E3%82%AF%E3%83%B3%E3%83%AA%E3%83%95%E3%83%AC%E3%83%83%E3%82%B7%E3%83%A5%E3%83%88%E3%83%BC%E3%82%AF%E3%83%B3id-%E3%83%88%E3%83%BC%E3%82%AF%E3%83%B3%E3%82%92%E6%88%BB%E3%81%99)" の方式で、アクセストークン、リフレッシュトークン、IDトークンをどのように使うかという話に進める。

## 2.6. アクセストークン、リフレッシュトークンを保存する

ID トークン、アクセストークン、リフレッシュトークンを保存する。

保存先は cookie や localStorage だと悪意あるスクリプトに読み込まれて悪用される可能性があるので、できれば避けたほうがいい。[Auth0 のベストプラクティス解説でもトークンをcookieなどのストレージに保存することは推奨していない](https://auth0.com/docs/secure/security-guidance/data-security/token-storage#browser-local-storage-scenarios)。

いろいろ調べた中だと、ログイン方法を調べる(=リバースエンジニアリングする)人は、Webブラウザと、認証サーバやAPサーバの間にプロキシを立てて、通信を傍受することで通信内容を解析しているようだ。レスポンスヘッダに Set-Cookie をセットして送ると、いくら AP サーバ側で HttpOnly フラグや Secure フラグを立ててもプロキシで比較的用意に判別できてしまうので、あまり防衛策にはなっていないようだ。またあたりまえだけどブラウザのディベロッパーコンソールにも表示されるので、それなりに知識がある人であればトークンは容易に取り出すことができてしまう。

また、Web ページを提供するサーバと AP サーバが異なるドメインの場合、AP サーバから提供される cookie はサードパーティ cookie になるため、最近のブラウザではデフォルトでブロックされるようになっており、この点からも cookie に保存するのはよい方法ではない。

ではどうすればよいかというと、[Javascript のクロージャや Web Worker のインメモリに保存しておくと比較的安全](https://auth0.com/docs/secure/security-guidance/data-security/token-storage#browser-in-memory-scenarios)とのこと。Auth0 だと ヘルパーライブラリでこのあたりをいい感じに扱ってくれるようだ。調べた限りだと Google ではそのようなことをサポートしてくれるライブラリはなさそうなので自前で実装するしかなさそう。

今回の例では私自身があまり詳しくないので cookie に保存している。参考にする場合は注意してください。

## 2.7. ユーザの自発的なログアウト

意図的にログアウトさせるには、[トークンを取り消し (revoke) ](https://developers.google.com/identity/protocols/oauth2/web-server#tokenrevoke)すればいい。 Google の場合アクセストークンを取り消すと、対応するリフレッシュトークンも無効になる。他の実装では挙動が違うかもしれないので注意。

## 2.8. 強制ログアウト、ユーザの無効化

ユーザの退職やトークンの漏えいなど、何かしらの理由でユーザの利用をやめさせたいときは、[Google クラウドコンソールのIAM管理画面](https://console.cloud.google.com/iam-admin/iam)で対象ユーザを取り除くことに加えて、そのユーザのトークンを revoke させる必要がある。revoke しないとリフレッシュトークンがユーザから消えるまでそのユーザはアプリケーションを使い続けることができてしまう。アクセストークン、リフレッシュトークンいずれでも revoke すればそれ以降トークンのチェックは失敗するようになる。

ただしそのためには AP サーバ側で何かしらトークンを記憶するための永続化手段を持たねばならず、インフラ側のコストが上昇する。特権管理者用のコマンドを用意する必要があるし、管理者が操作を忘れる可能性もある。

今回この部分の実装は入っていない。

# 3. 参考資料

いろんな人がいろんな話を書いているが、それらの情報とともに一度は OAuth2.0 の RFC である [RFC 6749](https://www.rfc-editor.org/rfc/rfc6749)[(日本語訳)](https://openid-foundation-japan.github.io/rfc6749.ja.html) を読み込んでみたほうがいいかもしれない。
