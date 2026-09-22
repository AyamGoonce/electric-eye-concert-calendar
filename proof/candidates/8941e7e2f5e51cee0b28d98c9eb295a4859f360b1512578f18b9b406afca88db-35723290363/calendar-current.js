(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.8941e7e2f5e51cee.js","sha256":"8941e7e2f5e51cee0b28d98c9eb295a4859f360b1512578f18b9b406afca88db","count":2133,"publishedAt":"2026-09-22T11:50:12Z","state":"calendar-state.json","stateSha256":"ea9d38dd32e7bcc9fb8447d623abb7fdf0dfb9103efa7a755f7c4e6f917e5c08","sourceState":"calendar-source-state.json","sourceStateSha256":"3c7ed26ddce78a5e037bc474990873c78b7be0a137a73a3fddbe62656d761158"});
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
