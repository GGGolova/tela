gapi.load('auth2', function() {
   auth2 = gapi.auth2.init({
      client_id: '549832843846-bje2kv1ag36aqgptn331f91f0ur4c61i.apps.googleusercontent.com'
   });
});
$('#signinButton').click(function() {
   auth2.grantOfflineAccess({
     'redirect_uri': 'postmessage'
   }).then(signInCallback);
});
function signInCallback(authResult) {
   if (authResult['code']) {
      $.ajax({
         type: 'POST',
         url: '/oauth/google',
         processData: false,
         data: JSON.stringify(authResult['code']),
         contentType: 'application/json; charset=utf-8',
         success: function(result) {
           location.reload();
         }
      });
   };
};
function signOut() {
   auth2.signOut().then(function() {
   });
   $.ajax({
      type: 'POST',
      url: '/logout',
      success: function(result) {
        location.reload();
      }
   });
};
