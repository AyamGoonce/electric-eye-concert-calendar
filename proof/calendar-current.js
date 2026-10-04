(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ac4a8b53997a6156.js","sha256":"ac4a8b53997a6156661d8d5bffcbe16663efb9add3f815797c61793b64abe39d","count":2182,"publishedAt":"2026-10-04T08:58:18Z","state":"calendar-state.json","stateSha256":"f63a4ddc54ad10a8d9befd75b70f925222fc7220b5a81fcbd8e8f38403481b12","sourceState":"calendar-source-state.json","sourceStateSha256":"347aee24f9b18b9afa5ddb1cb537fb0af393d24a188077b100abae910cfabb01"});
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
