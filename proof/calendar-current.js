(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.df1b0008266af098.js","sha256":"df1b0008266af098c64a9eea9630cfd89d7ddfc5cca4f260f67b96e4aa5927b3","count":2048,"publishedAt":"2026-10-25T10:00:06Z","state":"calendar-state.json","stateSha256":"8a37904112db942cde18c30f7f5eb49885c5e50ca45fee0dad1942205d3b7e69","sourceState":"calendar-source-state.json","sourceStateSha256":"cf463c3738bbc546f819f98a7fc086ef32f4863b464edce538266bc8fb18dd8c"});
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
