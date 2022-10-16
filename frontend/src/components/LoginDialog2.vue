<template>
    <v-main>
        <v-sheet class="ma-16">
            <v-form id="login">
                <v-container fluid>
                    <v-row>
                        <v-col class="text-center">
                            <div class="text-h4 ma-4 text-center">ログイン</div>
                            <!-- ログイン成功時に IDトークン を戻す場合
                                 https://yobaji.github.io/vue3-google-login/#googlelogin-component
                            <GoogleLogin :callback="callback"/>
                             -->
                            <!-- ログイン成功時に認証コードを戻す場合
                                 https://yobaji.github.io/vue3-google-login/#custom-button-as-slot -->
                            <GoogleLogin :callback="callback">
                                <v-btn style="height:55px;width:210px">
                                    <img src="/assets/btn_google_signin_light_normal_web@2x.png"  style="height:50px"/>
                                </v-btn>
                            </GoogleLogin>
                        </v-col>
                    </v-row>
                </v-container>
            </v-form>
        </v-sheet>
    </v-main>
</template>

<script>
import { useRouter } from 'vue-router'
import { verifyAuthCode } from '@/apis/auth/gentoken'

export default {
    name: 'LoginDialog2',
    setup() {
        const router = useRouter()
        const callback = async (response) => {
            verifyAuthCode(response.code)
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
</script>

<style>
#login {
    margin: 100px;
    width: 400px;
    border-radius: 10px;
    border: 1px solid #ccc;
    margin: 0 auto;
}
</style>