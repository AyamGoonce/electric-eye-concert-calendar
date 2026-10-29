(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.026f4474dfc273d1.js","sha256":"026f4474dfc273d12535f5d0e1d531c295c4237a348261837fb6875d9076f6b1","count":2034,"publishedAt":"2026-10-29T01:03:08Z","state":"calendar-state.json","stateSha256":"1e8e117c9e0c499cc297888fb53e22aad6ff4dd89bf57320a3be1121fccc6942","sourceState":"calendar-source-state.json","sourceStateSha256":"b28a3c5c9db8a372e991b63127d2c92cbcd01310afe3f45ab3edbd6054c10c2f"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
