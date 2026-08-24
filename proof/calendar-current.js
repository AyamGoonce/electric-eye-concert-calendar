(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.9c0f1ad58cec79d7.js","sha256":"9c0f1ad58cec79d7a76c82462277611a02d2db1f2986907d022f5102c0b8949c","count":1726,"publishedAt":"2026-08-24T02:02:46Z","state":"calendar-state.json","stateSha256":"6cc4578e45c4f0fdcc011c1c77bca4924a5b1c7991d4197fcb6be4b990c88207"});
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
