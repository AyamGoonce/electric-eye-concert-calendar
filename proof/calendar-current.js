(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.5374422c484e987d.js","sha256":"5374422c484e987dd5579279412b9545da1b7ea4d4e9c89e0cf090f9909864e1","count":2146,"publishedAt":"2026-09-23T17:15:38Z","state":"calendar-state.json","stateSha256":"31add35494a0369631dc0a0962d92a56dc9c5c6254c5cbbebe595bc8f1541482","sourceState":"calendar-source-state.json","sourceStateSha256":"517ca15fefe773279cca3bff7b8a5dc3e1038358df53f0c541eb1a8e48ee517b"});
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
