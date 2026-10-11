(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.8d3e33dd260afaae.js","sha256":"8d3e33dd260afaae30f007199fb9be2bc03bd56004c10c4a5d84de6979b8665a","count":2166,"publishedAt":"2026-10-11T19:37:20Z","state":"calendar-state.json","stateSha256":"d8db1bb323db88dc65ebf7531507b25519e8f319933bc84f87f8ebb444c0b8d8","sourceState":"calendar-source-state.json","sourceStateSha256":"bfafc18a8327dc0620a73ad1cab19f35fad0075d5753e391aab84234daa3379b"});
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
