(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b579fc6090707594.js","sha256":"b579fc6090707594a59dfe4736f3f92e35d397927b2f280e673611a9be15229b","count":2100,"publishedAt":"2026-11-16T14:12:35Z","state":"calendar-state.json","stateSha256":"8f32d94ec2d5f948627a3e11bc937a15c45e34e7a0b9ddbc3d895ad856900df2","sourceState":"calendar-source-state.json","sourceStateSha256":"abd79ee8b7b17d4f04e3ac15cd72ca4a12f5624bccd46b0d3b0a3b19bb5a774e"});
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
