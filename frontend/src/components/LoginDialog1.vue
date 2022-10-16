<template>
    <v-main>
        <v-sheet class="ma-16">
            <v-form id="login">
                <v-container fluid>
                    <v-row>
                        <v-col class="text-center">
                            <div class="text-h4 ma-4 text-center">ログイン</div>
                            <!-- ログイン成功時に IDトークン を戻す場合
                                 https://yobaji.github.io/vue3-google-login/#googlelogin-component -->
                            <GoogleLogin :callback="callback"/>
                            <!-- ログイン成功時に認証コードを戻す場合
                                 https://yobaji.github.io/vue3-google-login/#custom-button-as-slot
                            <GoogleLogin :callback="callback">
                                <button>
                                    <img src="/assets/btn_google_signin_light_normal_web@2x.png"  style="height:50px"/>
                                </button>
                            </GoogleLogin> -->
                        </v-col>
                    </v-row>
                </v-container>
            </v-form>
        </v-sheet>
    </v-main>
</template>

<script>
import { useCookies } from 'vue3-cookies'
import { verifyAuthCredential } from '@/apis/auth/gentoken'
export default {
    name: 'LoginDialog1',
    setup() {
        // const router = useRouter()
        const callback = async (response) => {
            console.log("Login response", response)
            const { cookies } = useCookies()
            cookies.set('id_token', response.credential)
            verifyAuthCredential(response.credential)
                .then((r) => {
                    console.log(r)
                    r.text().then((b) => { console.log(JSON.parse(b)) })
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