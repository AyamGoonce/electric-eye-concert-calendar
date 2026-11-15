(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e137f475bbf66ea8.js","sha256":"e137f475bbf66ea870639fdc9793391f507218e8514f7160c4b882ac77524add","count":2101,"publishedAt":"2026-11-15T17:39:02Z","state":"calendar-state.json","stateSha256":"0e39aa902d25c037bdc972eef0888437a67d7512585b383820671cb27efbbcc1","sourceState":"calendar-source-state.json","sourceStateSha256":"5739bf2a56926edc5c42a965d7b034fdb3d5995cef97d5fcc0e1fec14a683c9e"});
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
