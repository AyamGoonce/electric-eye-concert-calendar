(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.f6d4aab298a1c6be.js","sha256":"f6d4aab298a1c6be5f26759155bc901f7df6fc2253765eb795cd1278be7e867f","count":2124,"publishedAt":"2026-09-25T14:41:27Z","state":"calendar-state.json","stateSha256":"353f13c86663f484d547fde8f71a1763c98192f8e1b74ccb9813e52c8b09a9b3","sourceState":"calendar-source-state.json","sourceStateSha256":"4c002b676df19f35dba830e3b8c18785c91f761f941e4f6c7f4e80b788d92b71"});
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
