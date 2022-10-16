import { AppOptions } from "@/appoptions"

export const verifyAuthCredential = async (cred) => {
    const response = await fetch(
        AppOptions().apiServerURL + '/auth/google/verifycredential',
        {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + cred,
                'Content-Type': 'application/json'
            }

        })
    return response
}

export const verifyAuthCode = async (cred) => {
    const response = await fetch(
        AppOptions().apiServerURL + '/auth/google/verifyauthcode',
        {
            method: 'POST',
            mode: 'cors',
            credentials: 'include',
            headers: {
                'Authorization': 'Bearer ' + cred,
                'Content-Type': 'application/json'
            }

        })
    return response
}

export const verifyToken = async () => {
    const response = await fetch(
        AppOptions().apiServerURL + '/auth/google/verifytoken',
        {
            method: 'POST',
            mode: 'cors',
            credentials: 'include',
            headers: {
                // 'Authorization': 'Bearer ' + accessToken,
                'Content-Type': 'application/json'
            }
        }
    )
    return response
}

export const refreshAccessToken = async () => {
    const response = await fetch(
        AppOptions().apiServerURL + '/auth/google/refreshaccesstoken',
        {
            method: 'POST',
            mode: 'cors',
            credentials: 'include',
            headers: {
                // 'Authorization': 'Bearer ' + refreshToken,
                'Content-Type': 'application/json'
            }
        }
    )
    return response
}

export const revokeToken = async () => {
    const response = await fetch(
        AppOptions().apiServerURL + '/auth/google/revoketoken',
        {
            method: 'POST',
            mode: 'cors',
            credentials: 'include',
            headers: {
                // 'Authorization': 'Bearer ' + refreshToken,
                'Content-Type': 'application/json'
            }
        }
    )
    return response
}
