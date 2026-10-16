(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.912c5d51c8b53f2b.js","sha256":"912c5d51c8b53f2b38b1ac739b0d7d57cf56c4c072e91703586c1e5e60c421ea","count":2136,"publishedAt":"2026-10-16T16:46:33Z","state":"calendar-state.json","stateSha256":"d1f7f96ac1b8dea7e32940bd54ea6c201ad695a87cb980a3910d2b69718b79de","sourceState":"calendar-source-state.json","sourceStateSha256":"23fd60930ee76171f018835d1abc364ae5f4931d9764bee115f1461b36486c7e"});
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
