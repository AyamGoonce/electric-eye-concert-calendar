(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.5845852c50dd98d9.js","sha256":"5845852c50dd98d986f2c665bd2e1f5cd98184435327d373e4fe4d8aaaf0638c","count":2062,"publishedAt":"2026-10-29T18:33:50Z","state":"calendar-state.json","stateSha256":"d742a5b1421cfb243114d4b0b5877472a4c6052bd3d1fd3ac0e85229938e762f","sourceState":"calendar-source-state.json","sourceStateSha256":"1ca655b1b2ca10fa4415d1af3449924711b17f96af560fca95cc40b95f6ca2de"});
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
