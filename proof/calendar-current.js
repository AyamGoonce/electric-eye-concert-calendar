(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b982a54fa616b01d.js","sha256":"b982a54fa616b01d019ff5d8cb30150eaadd8bc5bc40fe7bf93fe4b443938d3a","count":2067,"publishedAt":"2026-08-29T16:52:36Z","state":"calendar-state.json","stateSha256":"a5d30998b1d1b75dc5a880127becbce9e99cf52af4527fe01e39599d7e1309d6"});
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
