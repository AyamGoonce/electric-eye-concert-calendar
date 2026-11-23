(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.bfe95f56aadcdfcf.js","sha256":"bfe95f56aadcdfcf29d7225e412b62bf8346e109c5d2b51b7a0840818bbfe097","count":2103,"publishedAt":"2026-11-23T13:01:34Z","state":"calendar-state.json","stateSha256":"3aa4e2db0acdde1c89d2a919f56e8ddf9896ea804a103ff9728880617315ba0e","sourceState":"calendar-source-state.json","sourceStateSha256":"616049a3dc1006898643eed07bff2b95129f0b6c7d85aaf66b0cec8f52696cf1"});
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
