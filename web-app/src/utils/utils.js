export async function callApi(apiPath, apiOptions = {}) {
    try {
        const apiBase = "https://renzil-obscure-journey-4jgxj447737wwq-3000.preview.app.github.dev";
        const fetchOptions = {
            headers: {},
        };
        if (apiOptions.method === "POST") {
            fetchOptions.method = "POST";
            fetchOptions.headers["Content-Type"] = "application/json";
        }
        if (apiOptions.body) {
            fetchOptions.body = apiOptions.body;
        }

        if (!apiOptions.noAuth) {
            let credentials = getCredentials();
            let { access, refresh } = credentials.tokens;
            if (Date.now() >= new Date(access.expires) && Date.now() < new Date(refresh.expires)) {
                await refreshTokens();
                credentials = getCredentials();
                ({ access, refresh } = credentials.tokens);
            }
            fetchOptions.headers["Authorization"] = `Bearer ${access.token}`;
        }
        return fetch(`${apiBase}${apiPath}`, fetchOptions)
            .then(response => response.json());
    } catch (e) {
        console.log(e);
    }
}

export async function refreshTokens() {
    const credentials = getCredentials();
    const { refresh } = credentials.tokens;

    const refreshResponse = await callApi("/v1/auth/refresh-tokens", {
        noAuth: true,
        method: "POST",
        body: JSON.stringify({
            "refreshToken": refresh.token,
        }),
    });

    setCredentials({
        user: credentials.user,
        tokens: refreshResponse.tokens,
    });
}

export function getCredentials() {
    return JSON.parse(window.localStorage.getItem("credentials") || "{}");
}

export function setCredentials(credentials) {
    window.localStorage.setItem("credentials", JSON.stringify(credentials));
}

export function b64DecodeUnicode(str) {
    str = str.replace(/-/g, '+').replace(/_/g, '/');
    // Going backwards: from bytestream, to percent-encoding, to original string.
    return decodeURIComponent(window.atob(str).split('').map(function (c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
}
