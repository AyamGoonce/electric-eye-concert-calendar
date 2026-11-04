(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b8131d8a833bd2ee.js","sha256":"b8131d8a833bd2ee897ff204cd6168d9b23dcad9c4868314bd58c2c7ddee82be","count":2051,"publishedAt":"2026-11-04T23:45:49Z","state":"calendar-state.json","stateSha256":"b533c0a2408ff99c7a4223c7264eb1fe7553c7039cfa35e2fef9d91eb8b9b486","sourceState":"calendar-source-state.json","sourceStateSha256":"371dd3d6cc9e161d1776c33b5523e16b502dd1b55867cbd386ad38db64a65a4b"});
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
