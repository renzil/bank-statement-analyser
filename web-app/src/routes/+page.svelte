<svelte:head>
   <script src="https://accounts.google.com/gsi/client" async defer>
   </script>
</svelte:head>
<script>
   import { onMount } from 'svelte';
   import { callApi, setCredentials, b64DecodeUnicode } from '../utils/utils';

   let isShowLoginButton = true;

   /* Events */

   onMount(async function load() {
      doGoogleSignInSetup();
      await doValidateToken();
   });

   async function onGoogleSignInCallback(response) {
      await doGoogleCredentialResponse(response);
   }

   function onValidateTokenOkay() {
      console.log("onValidateTokenOkay");
      doHideLoginButton();
   }

   function onValidateTokenNotOkay() {
      console.log("onValidateTokenNotOkay");
      doShowLoginButton();
   }

   function onValidateTokenError(e) {
      console.log("onValidateTokenError");
      doShowLoginButton();
   }

   function onUploadButtonClick() {
      doPdfFileSelect();
   }

   /* Actions */

   async function doValidateToken() {
      try {
            const validateResponse = await callApi("/v1/auth/validate-token", {
               method: "POST",
            });
            if (validateResponse.status === "ok") {
               onValidateTokenOkay();
            } else {
               onValidateTokenNotOkay();
            }
      } catch (e) {
            console.log(e);
            onValidateTokenError(e);
      }
   }

   function doGoogleSignInSetup() {
      google.accounts.id.initialize({
            client_id: "419266631077-7e3r3k96neg1upb7vv1kjoj5cqqr1ei0.apps.googleusercontent.com",
            callback: onGoogleSignInCallback,
      });
   }

   async function doGoogleCredentialResponse(response) {
      console.log(response);

      const jwtParts = response.credential.split('.');
      const jwtPayload = jwtParts[1];
      console.log(jwtPayload);
      const jwtPayloadDecoded = b64DecodeUnicode(jwtPayload);
      console.log(jwtPayloadDecoded);
      const responsePayload = JSON.parse(jwtPayloadDecoded);

      console.log("ID: " + responsePayload.sub);
      console.log('Full Name: ' + responsePayload.name);
      console.log('Given Name: ' + responsePayload.given_name);
      console.log('Family Name: ' + responsePayload.family_name);
      console.log("Image URL: " + responsePayload.picture);
      console.log("Email: " + responsePayload.email);
      const loginResponse = await callApi("/v1/auth/google-login", {
            noAuth: true,
            method: "POST",
            body: JSON.stringify({ credential: response.credential }),
      });

      setCredentials(loginResponse);
      doHideLoginButton();
   }

   function doShowLoginButton() {
      isShowLoginButton = true;
      google.accounts.id.renderButton(
            document.getElementById("googleSignInButtonDiv"),
            {
               theme: "outline",
               size: "large"
            }
      );
   }

   function doHideLoginButton() {
      isShowLoginButton = false;
   }

   async function doPdfFileSelect() {
      try {
         const pickerOpts = {
            types: [
               {
                  description: 'PDF Documents',
                  accept: {
                     'application/pdf': ['.pdf']
                  }
               },
            ],
            excludeAcceptAllOption: true,
            multiple: false
         };
         
         let [fileHandle] = await window.showOpenFilePicker(pickerOpts);

         console.log(fileHandle);

      } catch (e) {
         console.log(e);
      }
   }

</script>
<h1 class="text-3xl font-bold">Bank Statement Parser</h1>
{#if isShowLoginButton}
<div id="googleSignInButtonDiv" class="w-full h-8">
</div>
{:else}
<button id="uploadStatementBtn" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" on:click={onUploadButtonClick}>
   Upload
</button>
{/if}