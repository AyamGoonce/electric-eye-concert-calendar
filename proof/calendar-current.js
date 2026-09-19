(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e917f6711d5f8722.js","sha256":"e917f6711d5f87228ee8c7466069db8e86a3074a969282b5de3762f815a2a6af","count":2193,"publishedAt":"2026-09-19T23:14:33Z","state":"calendar-state.json","stateSha256":"491531907ce05b33eef5488e30002c1ac6b984d16fd2635b73a1048ced6993d3"});
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
