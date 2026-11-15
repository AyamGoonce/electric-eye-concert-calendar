(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.27be400adfa93bc8.js","sha256":"27be400adfa93bc805b488ab8a15f2521914a2b6f4230dbd2fa88807fc7e2d08","count":2109,"publishedAt":"2026-11-15T23:16:54Z","state":"calendar-state.json","stateSha256":"ebb9c1f7ae5ba1dae7dded599ad87f173ca9253a4a98c0885172e2dd058bd881","sourceState":"calendar-source-state.json","sourceStateSha256":"b14d92bdd899d3c2a4b438c8238bcff33845d459f8440d448a192a69953dec28"});
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
