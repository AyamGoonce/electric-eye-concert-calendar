(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e13ca9e809f853ce.js","sha256":"e13ca9e809f853ce5206484c89d4904418480ab20fc01068904d72cbeb161968","count":2100,"publishedAt":"2026-09-20T17:25:09Z","state":"calendar-state.json","stateSha256":"fcd12b59a5dd0fe3fdaf14b14fb68dacc9d6933271980cb43ba463d1308ac13e"});
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
