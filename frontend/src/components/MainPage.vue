<template>
    <v-main>
        <p>main</p>
        <p>
            <span> Expires in {{ expirein.a }} seconds</span>
        </p>
        <p><v-btn @click="onLogoutClick()">ログアウト</v-btn></p>
    </v-main>
</template>

<script>
import { verifyToken, refreshAccessToken, revokeToken } from '@/apis/auth/gentoken'
import { useRouter } from 'vue-router'
import { expireCounterStore } from '@/plugins/loginstatusstore'
import { onBeforeMount, reactive } from 'vue'

export default {
    name: 'MainPage',
    setup () {
        const router = useRouter()
        const store = expireCounterStore()
        const from = new Date()
        let expirein = reactive({a:0})

        // タイマー設定 - アクセストークンが期限切れになるまでの秒を更新
        setInterval(() => {
            const now = new Date()
            expirein.a = parseInt((from.getTime()/1000) + store.expire - (now.getTime()/1000))
            // アクセストークンが期限切れになったら自動的にページをリロードする
            if (expirein.a < 0) {
                location.reload()
            }
        }, 1000)

        const onLogoutClick = () => {
            revokeToken()
                .then(() => {
                    console.log('revoke success')
                    router.push({'name': 'LoginDialog2'})
                }).catch(() => {
                    console.log('revoke failed')
                })
        }

        // onBeforeMount
        onBeforeMount(() => {
            console.log('main beforemount')

            // ページ表示前にアクセストークンの確認を行う
            verifyToken()
                .then((r) => {
                    console.log('access token verified')
                    console.log('response status', r.status, r.statusText)
                    r.text().then((b) => { 
                        console.log('response body', JSON.parse(b))
                        store.setExpire(parseInt(JSON.parse(b).expires_in))
                    })
                }).catch((e) => {
                    // return code が 200 以外の場合はエラー
                    console.log('access token verify failed')
                    console.log('return status: ', e.status, e.statusText)

                    // リフレッシュトークンを使ってアクセストークンの更新を試みる
                    refreshAccessToken()
                        .then((r) => {
                            // 更新成功
                            console.log('access token refresh succeeded')
                            console.log('return status: ', r.status, r.statusText)
                            r.text().then((b) => {
                                store.setExpire(parseInt(JSON.parse(b).expires_in))
                            })
                        }).catch((e) => {
                            // 更新に失敗したらログインページに遷移
                            console.log('access token refresh failed')
                            console.log('return status: ', e.status, e.statusText)
                            router.push({'name': 'LoginDialog2'})
                        })
                })
        })

        return {
            expirein, onLogoutClick
        }
    }
}
</script>
