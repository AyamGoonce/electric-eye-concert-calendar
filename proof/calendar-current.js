(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.4415643a6d5a3371.js","sha256":"4415643a6d5a3371daef08dee5254335bb0ceb30d3644c5f407ec090437b666b","count":2232,"publishedAt":"2026-09-30T20:33:02Z","state":"calendar-state.json","stateSha256":"1c5f8feb538f503985cdfdebbcd624405453baabee7901b33556b7cc7c40ad27","sourceState":"calendar-source-state.json","sourceStateSha256":"edab750d3cc6a3066098b574d1f9bb1e807e807d684bc973e279981988732e19"});
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
