(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.445d15dc990ac84f.js","sha256":"445d15dc990ac84fda71de80a6ae09c2381bd99403f440a39a8394ca85985a12","count":2195,"publishedAt":"2026-10-07T06:09:52Z","state":"calendar-state.json","stateSha256":"699e583149361d5133796de3f9656375a366ab9a97059eedcaf08fb8f1f60342","sourceState":"calendar-source-state.json","sourceStateSha256":"e97b85d74bd4568cbea2a031442a9720598a390d781e409ef474c7a31e32f936"});
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
