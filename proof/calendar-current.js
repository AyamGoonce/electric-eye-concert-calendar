(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e7c5c80372e3a938.js","sha256":"e7c5c80372e3a938228d30fcaa65b11f58eaba57d46cf276263033dab6ccb7e8","count":2142,"publishedAt":"2026-09-22T17:01:11Z","state":"calendar-state.json","stateSha256":"3125485a4ad5f9b87f121aa6147d177e125cb4b9e5325441c9582b108128534d","sourceState":"calendar-source-state.json","sourceStateSha256":"ab25698574b814d0cda650d19d25519c234afd416989752007583ac4c7ea925e"});
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
