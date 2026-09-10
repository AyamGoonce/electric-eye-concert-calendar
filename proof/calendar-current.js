(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b040325d70c25e00.js","sha256":"b040325d70c25e00a5b9a1cb870bcc0ec621b83ee13e05ef15b557101ea89af4","count":2490,"publishedAt":"2026-09-10T11:30:53Z","state":"calendar-state.json","stateSha256":"f2b16b7d2a7433f7ac0ad7f2626b84a8d3a18cfc024740abcae7380da941259d"});
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
