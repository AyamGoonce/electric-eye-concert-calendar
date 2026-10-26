(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.7b529e3db8c71daa.js","sha256":"7b529e3db8c71daa1b2e4bb72f3aea37f10ff2f8e4108fccfd4aad5bb058440f","count":2046,"publishedAt":"2026-10-26T20:36:13Z","state":"calendar-state.json","stateSha256":"d15d8c06bfdefde4e97dceb5b8ab09d6a7f173919a59ff48cd0548a0b2de057a","sourceState":"calendar-source-state.json","sourceStateSha256":"8bf9191f57bef6e6227b9755506c74545aa904659f8690638e8911e63cd0a6c0"});
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
