/**
 * Copyright 2018, Google LLC
 * Licensed under the Apache License, Version 2.0 (the `License`);
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an `AS IS` BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// [START gae_python38_log]
'use strict';


window.addEventListener('load', function () {

    var logout = document.getElementById("sign-out")
    if (logout) {
        logout.addEventListener('click', logOut)
    }

    function logOut() {
        firebase.auth().signOut();
        window.location.href = "/index"
        console.log("Sign out js")
    };

    // FirebaseUI config.
    var uiConfig = {
        signInSuccessUrl: '/',
        signInOptions: [
            firebase.auth.GoogleAuthProvider.PROVIDER_ID,
            firebase.auth.EmailAuthProvider.PROVIDER_ID,
        ],
        tosUrl: '<your-tos-url>'
    };

    firebase.auth().onAuthStateChanged(function (user) {
        if (user) {

            console.log(`Signed in as ${user.displayName} (${user.email})`);
            user.getIdToken().then(function (token) {
                // Add the token to the browser's cookies. The server will then be
                // able to verify the token against the API.
                // SECURITY NOTE: As cookies can easily be modified, only put the
                // token (which is verified server-side) in a cookie; do not add other
                // user information.
                document.cookie = "token=" + token;
            });
        } else {
            // User is signed out.
            // Initialize the FirebaseUI Widget using Firebase.
            var ui = new firebaseui.auth.AuthUI(firebase.auth());
            // Show the Firebase login button.
            var checkAuth = document.querySelector('#firebaseui-auth-container') !== null;
            if(checkAuth){
                ui.start('#firebaseui-auth-container', uiConfig);
            }
            // Clear the token cookie.
            document.cookie = "token=";
        }
    }, function (error) {
        console.log(error);
        alert('Unable to log in: ' + error)
    });
});
