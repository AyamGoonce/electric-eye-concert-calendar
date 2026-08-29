(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.599c65837b2b28a8.js","sha256":"599c65837b2b28a87ca60b073b951f47dbf3b77e97df8cfb9946bf657d0de957","count":2065,"publishedAt":"2026-08-29T21:06:53Z","state":"calendar-state.json","stateSha256":"e9bb32ffd0041358633e8a4d1a14764d625f1ae758685d4e91185c595d83d80d"});
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
