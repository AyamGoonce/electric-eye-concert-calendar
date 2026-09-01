(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e2069e5841dcf7f9.js","sha256":"e2069e5841dcf7f91c4cc558457c1c61b8f6085d02113a561314bf2c7ac9c4fb","count":2169,"publishedAt":"2026-09-01T20:05:54Z","state":"calendar-state.json","stateSha256":"80b5f4fe06a16959fcf8826f2ff602f9968700844f3543912650db29c3ffe018"});
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
