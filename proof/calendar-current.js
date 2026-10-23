(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.f3ea10f2803b0e60.js","sha256":"f3ea10f2803b0e6075225ddeeccfd40335ae9eeafff2b8c790e917a3d3d29cb3","count":2069,"publishedAt":"2026-10-23T05:01:43Z","state":"calendar-state.json","stateSha256":"45121a3279d65a2c9b6d504fecfc46cb3aef5432af8cab826a5810436fa5c72b","sourceState":"calendar-source-state.json","sourceStateSha256":"f6bc9e5fc1ac114768bddcc7c52eccbe9e8e6f23a6a4d236cf25d767109790c1"});
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
