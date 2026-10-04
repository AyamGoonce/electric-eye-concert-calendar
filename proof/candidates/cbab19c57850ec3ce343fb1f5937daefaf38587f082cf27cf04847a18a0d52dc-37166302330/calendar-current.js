(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.cbab19c57850ec3c.js","sha256":"cbab19c57850ec3ce343fb1f5937daefaf38587f082cf27cf04847a18a0d52dc","count":2182,"publishedAt":"2026-10-04T00:54:45Z","state":"calendar-state.json","stateSha256":"b8b48b045dcbae54450ef6ba74e09c780dd6723070975e611c29e0c843103f0c","sourceState":"calendar-source-state.json","sourceStateSha256":"f7d534a3e4dfd7bf80a3adb20ad5b9448f09901c338bf18c9297e57b99f00847"});
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
