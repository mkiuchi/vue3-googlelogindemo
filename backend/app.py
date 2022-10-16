import json
import requests as rq
from urllib.parse import quote
from flask import Flask, jsonify, make_response, request, abort
from flask_cors import CORS, cross_origin
from google.oauth2 import id_token
from google.auth.transport import requests
app = Flask(__name__)
CORS(app)
#CORS(app, resources={"*": {"origins": ["http://localhost:8080"]}}, supports_credentials=True)

client_id = "クライアントID"

@app.route('/auth/google/verifycredential', methods=['POST'])
#@cross_origin(supports_credentials=True)
def verifyCredential():
    # クレデンシャル(=IDトークン)を検証し、プロファイル情報を戻す
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

@app.route('/auth/google/verifytoken', methods=['POST'])
@cross_origin(supports_credentials=True, methods=['POST'], origin="http://localhost:8080")
def verifyAuthToken():
    print("verify token")
    access_token = "null"
    access_token = request.cookies.get("access_token")
    
    # アクセストークンがなかった場合は 403 Forbidden を返す
    if access_token == "null":
        abort(403, description="No access token is given.")

    # アクセストークンが空でなかった場合は検証する
    url = "https://oauth2.googleapis.com/tokeninfo" + \
        '?access_token=' + access_token
    r = rq.get(url)
    if r.status_code != 200:
        abort(403, description=r.text)
    ret = make_response(jsonify({"expires_in": json.loads(r.text)["expires_in"]}))

    return ret, 200


@app.route('/auth/google/refreshaccesstoken', methods=['POST'])
@cross_origin(supports_credentials=True, methods=['POST'], origin="http://localhost:8080")
def refreshAccessToken():
    #refresh_token = request.headers["Authorization"][7:]
    print("refresh access token")
    refresh_token = "null"
    refresh_token = request.cookies.get("refresh_token")
    print("refresh token", refresh_token)

    # アクセストークンがなかった場合は 403 Forbidden を返す
    if refresh_token == "null":
        abort(403, description="No refresh token is given.")

    url = "https://oauth2.googleapis.com/token"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'charset': "UTF-8"
    }
    content = 'client_id=クライアントID'
    content += '&client_secret=クライアントシークレット'
    content += '&refresh_token=' + refresh_token
    content += '&grant_type=refresh_token'

    r = rq.post(url, data=content, headers=headers)
    if r.status_code != 200:
        abort(403, description=r.text)
    body = json.loads(r.text)
    ret = make_response(
        jsonify({
            "message": "access token refresh succeeded",
            "expires_in": body["expires_in"]
        }))
    ret.headers.add("Set-Cookie", "access_token="+body["access_token"]+"; SameSite=None; Max-Age=86400; HttpOnly; Secure; Path=/")
    ret.headers.add("Set-Cookie", "id_token="+body["id_token"]+"; SameSite=None; Max-Age=86400; HttpOnly; Secure; Path=/")
    return ret, 200


@app.route('/auth/google/revoketoken', methods=['POST'])
@cross_origin(supports_credentials=True, methods=['POST'], origin="http://localhost:8080")
def revokeToken():
    print("revoke token")
    access_token = "null"
    access_token = request.cookies.get("access_token")
    print("access token", access_token)

    # アクセストークンがなかった場合は 403 Forbidden を返す
    if access_token == "null":
        abort(403, description="Access token is invalid.")

    url = "https://oauth2.googleapis.com/revoke"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'charset': "UTF-8"
    }
    content = 'token=' + access_token

    r = rq.post(url, data=content, headers=headers)
    if r.status_code != 200:
        abort(403, description=r.text)
    body = json.loads(r.text)
    ret = make_response(jsonify({ "message": "access token successfully revoked"}))
    ret.headers.add("Set-Cookie", "access_token=; SameSite=None; Max-Age=-1; HttpOnly; Secure; Path=/")
    ret.headers.add("Set-Cookie", "refresh_token=; SameSite=None; Max-Age=-1; HttpOnly; Secure; Path=/")
    ret.headers.add("Set-Cookie", "id_token=; SameSite=None; Max-Age=-1; HttpOnly; Secure; Path=/")
    return ret, 200
