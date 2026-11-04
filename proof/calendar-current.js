(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.bd04bd0fe3774dd4.js","sha256":"bd04bd0fe3774dd4394f8c2aa20cef4e0b3eca333a82115c35603a7e51466f7f","count":2037,"publishedAt":"2026-11-04T08:36:05Z","state":"calendar-state.json","stateSha256":"4ae46d851f33a244e36c3d08b80dc38a06ab5e55695e6d469a45cc90cabc73a2","sourceState":"calendar-source-state.json","sourceStateSha256":"a1eac771ffdc9b8c209e2be3384b3c53ef8e934beec33303bd7a8e77d2716e02"});
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
