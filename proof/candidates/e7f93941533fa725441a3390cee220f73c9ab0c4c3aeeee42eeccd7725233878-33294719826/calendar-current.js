(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e7f93941533fa725.js","sha256":"e7f93941533fa725441a3390cee220f73c9ab0c4c3aeeee42eeccd7725233878","count":2061,"publishedAt":"2026-08-30T05:45:16Z","state":"calendar-state.json","stateSha256":"84322b7878d23b3363ec752ebf704ab7d51734c937fa158c2407e75fa10135a3"});
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
