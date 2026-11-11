(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.fa0d03f2e8fd78db.js","sha256":"fa0d03f2e8fd78db9be8b32629a903f02d9731b3e16d6fbc29b81f28cd96c1c6","count":2195,"publishedAt":"2026-11-11T06:36:51Z","state":"calendar-state.json","stateSha256":"3ba0eba946fd550e8f081525fa5dd3d1cffa45ba1672a978ee0597559be3e0c3","sourceState":"calendar-source-state.json","sourceStateSha256":"72e5e6dd5e929137f2eb5350e4596b1bee2d851e81e3c749abaa5448924492f6"});
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
