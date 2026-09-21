(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a38d3e511e05c682.js","sha256":"a38d3e511e05c682c7ffa20eeef5977a8089851ab2f28105a063830713a6fa79","count":2131,"publishedAt":"2026-09-21T20:04:13Z","state":"calendar-state.json","stateSha256":"59581725846878d09fa3f28f3551bac8e597ca966e44aa56a877589c91ea4108"});
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
