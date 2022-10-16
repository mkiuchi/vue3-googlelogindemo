import { defineStore } from 'pinia'

export const loginStatusStore = defineStore({
    id: 'loginStatusStore',
    state: () => ({
        responseStatus: null
    }),
    actions: {
        set(newval) {
            this.responseStatus = newval
        }
    }
})

export const expireCounterStore = defineStore({
    id: 'expireConterStore',
    state: () => ({
        from: new Date(),
        now: new Date(),
        expire: 0,
        expirein: 0
    }),
    actions: {
        setFrom(newval) { this.from = newval },
        setNow(newval) { this.now = newval },
        setExpire(newval) { this.expire = newval },
        setExpirein(newval) { this.expirein = newval }
    }
})