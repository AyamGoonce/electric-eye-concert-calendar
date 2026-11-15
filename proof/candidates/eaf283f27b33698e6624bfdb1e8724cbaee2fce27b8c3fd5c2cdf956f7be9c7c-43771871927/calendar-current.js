(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.eaf283f27b33698e.js","sha256":"eaf283f27b33698e6624bfdb1e8724cbaee2fce27b8c3fd5c2cdf956f7be9c7c","count":2104,"publishedAt":"2026-11-15T22:54:55Z","state":"calendar-state.json","stateSha256":"4e2a0098a71111bf71097e7accceea6d88d3b1c62ddab5bb42a48266767eabb0","sourceState":"calendar-source-state.json","sourceStateSha256":"8bd81388ffdae44b0fba9e6bff24a5f64288c0110cb267f15527e6a7580f6ed7"});
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
