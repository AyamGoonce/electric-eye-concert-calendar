(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.83eb9f90ba091eee.js","sha256":"83eb9f90ba091eee5809bb3a2f20f3d8682544a2cbc2171610c98e4531333216","count":2220,"publishedAt":"2026-10-07T20:41:26Z","state":"calendar-state.json","stateSha256":"40201a1b1d2f464f18600e21535774f33e55fbaccf82fdb6d8774f4052f8ea81","sourceState":"calendar-source-state.json","sourceStateSha256":"7f39cfc62acfeb5a4e3aba89d67629911c676a0bdf19dd3fd5a6bf4553197e73"});
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
